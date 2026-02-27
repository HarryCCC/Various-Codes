Attribute VB_Name = "模块1"
Sub ResizeCenterCleanAndResetIndentImages()
    '==================================================
    ' 功能：(多合一终极版)
    ' 1. 宽度统一为 16cm
    ' 2. (嵌入型) 移除图片同一行中、位于图片前的所有空格和制表符
    ' 3. (嵌入型) 将图片所在段落的左右缩进、首行缩进全部清零
    ' 4. 将所有图片（及其段落）设置为水平居中
    '
    ' 警告：运行前请备份文档，此操作无法撤销。
    '==================================================
    
    ' --- 宽度常量 ---
    Const MyTargetWidth_CM As Single = 16

    Dim targetWidthInPoints As Single
    Dim oShape As Shape
    Dim iShape As InlineShape
    Dim countShapes As Long
    Dim countInlineShapes As Long
    Dim preImageRange As Range
    Dim paraRange As Paragraph
    
    ' 厘米转磅
    targetWidthInPoints = CentimetersToPoints(MyTargetWidth_CM)
    
    countShapes = 0
    countInlineShapes = 0
    
    ' === 1. 处理所有“浮动型”图片 (Shapes) ===
    '    (使其相对于“页边距”居中)
    For Each oShape In ActiveDocument.Shapes
        If oShape.Type = msoPicture Or oShape.Type = msoLinkedPicture Then
            
            ' (1) 调整宽度
            oShape.LockAspectRatio = msoTrue
            oShape.Width = targetWidthInPoints
            
            ' --- (2) 设置居中 (浮动型) ---
            '     将其定位基准设为“页边距”
            oShape.RelativeHorizontalPosition = wdRelativeHorizontalPositionMargin
            '     将其在基准上的位置设为“居中”
            oShape.Left = wdShapeCenter
            
            countShapes = countShapes + 1
        End If
    Next oShape

    ' === 2. 处理所有“嵌入型”图片 (InlineShapes) ===
    '    (清理空格 -> 缩进归零 -> 居中)
    For Each iShape In ActiveDocument.InlineShapes
        If iShape.Type = wdInlineShapePicture Or iShape.Type = wdInlineShapeLinkedPicture Then
            
            ' (1) 调整宽度
            iShape.LockAspectRatio = msoTrue
            iShape.Width = targetWidthInPoints
            
            ' (2) 获取图片所在的段落
            Set paraRange = iShape.Range.Paragraphs(1)
            
            ' --- (3) 清理图片前的空格和制表符 ---
            Set preImageRange = ActiveDocument.Range(paraRange.Range.Start, iShape.Range.Start)
            ' 检查这个范围内的文本是否“全是”空白符
            If Trim(preImageRange.Text) = "" Then
                ' 如果全是空白，则安全地清空它
                preImageRange.Text = ""
            End If
            
            ' --- (4) 缩进归零并设置居中 (嵌入型) ---
            With paraRange.Format
                .LeftIndent = 0         ' 缩进归零 (要求3)
                .RightIndent = 0        ' 缩进归零 (要求3)
                .FirstLineIndent = 0    ' 缩进归零 (要求3)
                .Alignment = wdAlignParagraphCenter ' 设为居中 (要求4)
            End With
            
            countInlineShapes = countInlineShapes + 1
        End If
    Next iShape

    ' === 3. 报告结果 ===
    MsgBox "处理完成！" & vbCrLf & vbCrLf & _
           "宽度统一设置为：" & MyTargetWidth_CM & " 厘米。" & vbCrLf & _
           "所有图片已居中。" & vbCrLf & _
           "所有图片段落的缩进已归零。" & vbCrLf & _
           "已清理嵌入式图片前的多余空格。" & vbCrLf & vbCrLf & _
           "浮动图片处理数量：" & countShapes & " 张" & vbCrLf & _
           "嵌入式图片处理数量：" & countInlineShapes & " 张", _
           vbInformation, "批量处理图片(终极版)"
           
End Sub


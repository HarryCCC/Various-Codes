Attribute VB_Name = "模块1"
Option Explicit

' 方法一：自动调整一个“固定”的特定区域
' ----------------------------------------------------------------
' 优点：精确控制范围。
' 缺点：如果数据范围变化，您需要手动修改代码中的 "A1:G20"。
' ----------------------------------------------------------------
Sub AutoFit_SpecificRange()
    ' --- 请将 "A1:G20" 修改为您需要调整的“特定区域” ---
    Const cTargetRange As String = "A1:G20"
    ' ----------------------------------------------------

    Dim ws As Worksheet
    Set ws = ThisWorkbook.ActiveSheet ' 目标：当前活动的工作表

    On Error Resume Next
    Dim rng As Range
    Set rng = ws.Range(cTargetRange)
    On Error GoTo 0
    
    If rng Is Nothing Then
        MsgBox "您定义的区域 '" & cTargetRange & "' 无效。", vbExclamation, "范围错误"
        Exit Sub
    End If

    ' 开始调整
    Application.ScreenUpdating = False ' 关闭屏幕刷新，加快速度
    
    With rng
        .Rows.AutoFit       ' 自动调整指定区域内所有行的行高
        .Columns.AutoFit    ' 自动调整指定区域内所有列的列宽
    End With
    
    Application.ScreenUpdating = True ' 重新开启屏幕刷新
    
    MsgBox "区域 '" & cTargetRange & "' 的行高和列宽已自动调整完毕。", vbInformation, "操作完成"
End Sub


' 方法二：自动调整“当前选中”的区域
' ----------------------------------------------------------------
' 优点：最灵活。您在 Excel 中选中哪个区域，宏就调整哪个区域。
' ----------------------------------------------------------------
Sub AutoFit_Selection()
    ' 检查用户是否真的选择了一个单元格区域
    If TypeName(Selection) <> "Range" Then
        MsgBox "请您先用鼠标在工作表中选择一个区域。", vbInformation, "未选择区域"
        Exit Sub
    End If
    
    Application.ScreenUpdating = False
    
    With Selection
        .Rows.AutoFit
        .Columns.AutoFit
    End With
    
    Application.ScreenUpdating = True
End Sub


' 方法三：自动调整当前工作表“所有已使用”的区域
' ----------------------------------------------------------------
' 优点：最自动化。自动检测您数据表(UsedRange)的边界。
' ----------------------------------------------------------------
Sub AutoFit_AllUsedData()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.ActiveSheet
    
    Application.ScreenUpdating = False

    ' ActiveSheet.UsedRange 会自动获取包含数据的所有单元格范围
    With ws.UsedRange
        .Rows.AutoFit
        .Columns.AutoFit
    End With
    
    Application.ScreenUpdating = True
    
    MsgBox "当前工作表的所有数据区域已自动调整。", vbInformation, "操作完成"
End Sub


Sub Main()
    Set WshShell = WScript.CreateObject("WScript.Shell")

    If WshShell.Popup("Add Query GRE Seats to startup? (this dialog will disappear in 6 seconds)", 6, "Query GRE Seats", 1) = 1 Then
        strBatPath = WshShell.CurrentDirectory & "\run.bat"
        strStartup = WshShell.SpecialFolders("Startup")

        Set oShellLink = WshShell.CreateShortcut(strStartup & "\Query GRE Seats.lnk")
        oShellLink.TargetPath = strBatPath
        oShellLink.WindowStyle = 7
        oShellLink.Description = "Query GRE Seats"
        oShellLink.WorkingDirectory = WshShell.CurrentDirectory
        oShellLink.Save
   
        WshShell.Popup "Add Query GRE Seats to startup successfully", 5, "Query GRE Seats", 0
    End If
End Sub

Main
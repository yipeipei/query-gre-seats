Sub Main()
    Set WshShell = WScript.CreateObject("WScript.Shell")
    
    If WshShell.Popup("Remove Query GRE Seats from startup? (this dialog will disappear in 6 seconds)", 6, "Query GRE Seats", 1) = 1 Then
        strStartup = WshShell.SpecialFolders("Startup")
		
		strShortcut = strStartup & "\Query GRE Seats.lnk"
        
		Set fso = CreateObject("Scripting.FileSystemObject")
		If fso.FileExists(strShortcut) Then fso.DeleteFile(strShortcut)
   
        WshShell.Popup "Remove Query GRE Seats from startup successfully", 5, "Query GRE Seats", 0
    End If
End Sub

Main
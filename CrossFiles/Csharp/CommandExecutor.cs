using System;
using System.Diagnostics;
using System.Linq;

public class CommandExecutor
{
    public static void ExecuteCommand(string userInput)
    {
        // Ensure input contains only alphanumeric characters and spaces
        if (!string.IsNullOrWhiteSpace(userInput) && userInput.All(c => char.IsLetterOrDigit(c) || c == ' '))
        {
            Process.Start("cmd.exe", "/C echo " + userInput);
        }
        else
        {
            Console.WriteLine("Invalid command! Only alphanumeric input is allowed.");
        }
    }
}

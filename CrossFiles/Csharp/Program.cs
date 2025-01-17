using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter a command: ");
        string userInput = Console.ReadLine();
        CommandExecutor.ExecuteCommand(userInput);

        Console.Write("Enter your username: ");
        string username = Console.ReadLine();
        DatabaseHandler dbHandler = new DatabaseHandler();
        dbHandler.FetchUserData(username);
    }
}

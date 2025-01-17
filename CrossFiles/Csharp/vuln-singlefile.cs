using System;
using System.Diagnostics;
using System.Data.SqlClient;

class Program
{
    static void Main()
    {
        Console.Write("Enter a command: ");
        string userInput = Console.ReadLine(); // Tainted user input

        // ⚠️ BAD: Directly passing user input to Process.Start (Command Injection)
        Process.Start("cmd.exe", "/C " + userInput); 

        Console.Write("Enter your username: ");
        string username = Console.ReadLine(); // Tainted user input

        // ⚠️ BAD: Using string concatenation in SQL query (SQL Injection)
        string connectionString = "Server=myServer;Database=myDB;User Id=myUser;Password=myPass;";
        using (SqlConnection conn = new SqlConnection(connectionString))
        {
            conn.Open();
            string sqlQuery = "SELECT * FROM Users WHERE username = '" + username + "'";
            using (SqlCommand cmd = new SqlCommand(sqlQuery, conn))
            {
                using (SqlDataReader reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine($"User found: {reader["username"]}");
                    }
                }
            }
        }
    }
}

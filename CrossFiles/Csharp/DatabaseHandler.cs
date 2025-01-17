using System;
using System.Data.SqlClient;

public class DatabaseHandler
{
    private string connectionString = "Server=myServer;Database=myDB;User Id=myUser;Password=myPass;";

    public void FetchUserData(string username)
    {
        using (SqlConnection conn = new SqlConnection(connectionString))
        {
            conn.Open();
            //string sqlQuery = "SELECT * FROM Users WHERE username = @username";
            string sqlQuery = "SELECT * FROM Users WHERE username = '" + username + "'";
            using (SqlCommand cmd = new SqlCommand(sqlQuery, conn))
            {
                cmd.Parameters.AddWithValue("@username", username); // Prevents SQL Injection
                
                using (SqlDataReader reader = cmd.ExecuteReader())
                {
                    if (reader.HasRows)
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine($"User found: {reader["username"]}");
                        }
                    }
                    else
                    {
                        Console.WriteLine("User not found.");
                    }
                }
            }
        }
    }
}

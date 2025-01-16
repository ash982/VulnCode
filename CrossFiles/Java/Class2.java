import java.sql.*;

public class Class2 {
    private String input;
    private Connection conn;

    public Class2(String input) {
        this.input = input;
    }

    public void connectDb(String dbUrl) {
        try {
            conn = DriverManager.getConnection(dbUrl);
        } catch (SQLException e) {
            System.out.println("Connection failed: " + e.getMessage());
        }
    }

    public void process() {
        System.out.println("Class2 processing: " + input);
        if (conn == null) {
            System.out.println("Database not connected");
            return;
        }

        // Potentially unsafe operation
        String query = "SELECT * FROM users WHERE username = '" + input + "'";
        System.out.println("Executing query: " + query);

        try {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(query);
            while (rs.next()) {
                System.out.println(rs.getString("username"));
            }
        } catch (SQLException e) {
            System.out.println("Query failed: " + e.getMessage());
        }
    }

    public void closeDb() {
        try {
            if (conn != null) {
                conn.close();
            }
        } catch (SQLException e) {
            System.out.println("Error closing connection: " + e.getMessage());
        }
    }
}

import org.apache.xmlrpc.webserver.WebServer;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.XmlRpcException;
import java.sql.*;
import java.util.Random;
import java.util.Vector;
import java.util.Scanner;
import java.util.HashMap;
import java.util.concurrent.locks.ReentrantLock;

public class Server {

    // Indices to help dissect resultSets
    static private int ID_INDEX = 0;
    static private int TITLE_INDEX = 1;
    static private int TOPIC_INDEX = 2;
    static private int STOCK_INDEX = 3;
    static private int PRICE_INDEX = 4;

    private final ReentrantLock lock = new ReentrantLock();
    static private HashMap<Integer, Integer> log = new HashMap<Integer, Integer>();
    static private Connection c = null;

    /*
     * Helper function that executes a query in the sql database
     */
    private static Vector<String[]> sqlExecuteQuery(String query) {
        Statement stmt = null;
        try {
            
            stmt = c.createStatement();
            ResultSet rs = stmt.executeQuery(query);
            Vector <String[]> result = new Vector<String[]>();

            if (rs != null) {
                while ( rs.next() ) {
                    String[] temp = {String.valueOf(rs.getInt("ID")),
                    rs.getString("TITLE"),
                    rs.getString("TOPIC"),
                    String.valueOf(rs.getInt("STOCK")),
                    String.valueOf(rs.getFloat("PRICE"))};
                    result.add(temp);
                }
            }
            rs.close();
            stmt.close();
            return result;
        } catch ( Exception e ) {
            System.err.println("Server sqlExecuteQuery Error: " + e.getMessage() );
            return null;
        }
    }

    /*
     * Helper function that does an execution in the sql database
     */
    private static Boolean sqlExecute(String execution) {
        
        Statement stmt = null;
        try {
            stmt = c.createStatement();
            Boolean value = false;
            Integer check = stmt.executeUpdate(execution);
            if (check > 0) {   
                value = true;
            }

            stmt.close();
            return value;
        } catch ( Exception e ) {
            System.err.println("Server sqlExecute Error: " + e.getMessage() );
            return null;
        }
    }

    /*
     * search(topic) - allows the user to specify a topic (or category)
     * and returns all entries belonging to that category (a title and an
     * item number are displayed for each match).
     */
    public Object[] search(String topic) {
        try {
            Vector<String[]> result = sqlExecuteQuery("SELECT * FROM BOOKS WHERE TOPIC = '" + topic + "';");

            Vector<String> status = new Vector<>();
            if (result.size() == 0) {
                status.add("Invalid topic");
            } else if (result == null){
                status.add("Database error... please try again shortly");
            } else {
                for (int i = 0; i < result.size(); i++) {
                    String[] book = result.get(i);
                    status.add(book[ID_INDEX] + "|" + book[TITLE_INDEX]);
                }
            }
            return status.toArray();
        } catch (Exception e ) {
            System.err.println("Server Search Error: " + e.getMessage());
            return null;
        }

    }

    /*
     * lookup(item_number) - allows an item number to be specified
     * and returns details such as title, cost, subject,
     * and whether or not the item is in stock.
     */
    public Object[] lookup(Integer item_number) {
        try {
            // retireiving book information from database
            Vector<String[]> result = sqlExecuteQuery("SELECT * FROM BOOKS WHERE ID = '" + item_number + "';");

            Vector<String> status = new Vector<>();
            if (result.size() == 0) {
                status.add("Invalid item number");
            } else if (result == null){
                status.add("Database error... please try again shortly");
            } else {
                 String[] book = result.get(0);
                // identifying whether a book is in stock
                if (Integer.parseInt(book[STOCK_INDEX]) > 0 ) {
                    status.add(book[TITLE_INDEX] + "|" + book[PRICE_INDEX] + "|" + book[TOPIC_INDEX] + "|In Stock");
                } else {
                    status.add(book[TITLE_INDEX] + "|" + book[PRICE_INDEX] + "|" + book[TOPIC_INDEX] + "|Out of Stock");
                }
            }
            return status.toArray();
        } catch (Exception e ) {
            System.err.println( "Server Lookup Error: " + e.getMessage() );
            return null;
        }

    }

    /*
     * buy(item_number) - specifies an item number for purchase
     * (assume the desired quantity is always 1).
     */
    public Object[] buy(Integer item_number) {
        try {
            lock.lock();
            Vector<String[]> result = sqlExecuteQuery("SELECT * FROM BOOKS WHERE ID = " + item_number + ";");
            Vector<String> status = new Vector<>();
            if (result.size() == 0) {
                status.add("Invalid item number");
            } else if (result == null){
                status.add("Database error... please try again shortly");
            } else { 
                // checks to see if the book is in stock
                if (Integer.parseInt(result.get(0)[STOCK_INDEX]) > 0){
                        //helper for  update
                            Boolean check = sqlExecute("UPDATE BOOKS SET STOCK = STOCK - 1 WHERE ID = " + item_number + ";");
                            if (check) {
                                if (log.containsKey(item_number)) {
                                    log.put(item_number, log.get(item_number) + 1);
                                } else {
                                    log.put(item_number, 1);
                                }
                                status.add("Successfully purchased");
                            } else {
                                status.add("Purchase Failed, please try again later");
                            } 
                } else {
                        status.add("Out of stock");
                }
                
            }
            lock.unlock();
            return status.toArray();
        } catch ( Exception e ) {
            System.err.println("Server Buy Error: " + e.getMessage() );
            return null;
        }
    }

    /*
     * restock(item_number) - update stocks for a specified book using
     * the books ID, the amount restocked is randomly generated from 10 to 50.
     */
    private static void restock(Integer item_number) {
        try {
            // Randomly generating the amount of books being restocked
            Random rand = new Random();
            int upperbound = 50;
            int lowerbound = 10;
            int restockAmt = rand.nextInt(upperbound - lowerbound) + lowerbound;

            // Updates the database
            Boolean check = sqlExecute("UPDATE BOOKS SET STOCK = STOCK + " + restockAmt + " WHERE ID = " + item_number + ";");
            if (check) {
                System.out.println("Restocked " + restockAmt + " books");
            } else if (!check) {
                System.out.println("Invalid Item Number");
            } else {
                System.out.println("Database error... please try again shortly");
            }

        } catch (Exception e) {
            System.err.println("Server Restock Error: " + e.getMessage() );
        }

    }

    /*
     * update(item_number, price) - update price for item.
     */
    private static void update(Integer item_number, Float price) {
        try {
            Boolean check = sqlExecute("UPDATE BOOKS SET PRICE = " + price + " WHERE ID = " + item_number + ";");
            if (check) {
                System.out.println("Book " + item_number + " price was updated to: " + price);
            } else if (!check) {
                System.out.println("Invalid Item Number or Price");
            } else {
                System.out.println("Database error... please try again shortly");
            }
        } catch(Exception e) {
            System.err.println("Update Error: " + e.getMessage() );
        }
    }

    /*
     * stock() - displays the current stock of books
     */
    private static void stock() {
        try {
            Vector<String[]> result = sqlExecuteQuery("SELECT * FROM BOOKS;");

            if (result == null){
                System.out.println("Database error... please try again shortly");
            } else {
                for (int i = 0; i < result.size(); i++) {
                    String[] book = result.get(i);
                    System.out.println(book[ID_INDEX] + "|" + book[TITLE_INDEX] + "|" + book[TOPIC_INDEX] + "|" + book[STOCK_INDEX] + "|" + book[PRICE_INDEX]);
                }
            }

        } catch(Exception e) {
            System.err.println("Stock error: " + e.getMessage() );
        }
    }

    private static void stringParser(String input) {
        String[] tokens = input.split(" ");
        switch(tokens[0]) {
            case "log":
                System.out.println(log);
                break;
            case "restock":
                if (tokens.length == 2) {
                    try {
                        restock(Integer.parseInt(tokens[1]));
                        break;
                    } catch (Exception e) {
                        System.out.println("Invalid request: restock <item_number>");
                        break;
                    }
                } else {
                    System.out.println("Invalid request: restock <item_number>");
                    break;
                }
            case "update":
                if (tokens.length == 3) {
                    try {
                        update(Integer.parseInt(tokens[1]), Float.parseFloat(tokens[2]));
                        break;
                    } catch (Exception e){
                        System.out.println("Invalid request: update <item_number> <price>");
                        break;
                    }
                } else {
                    System.out.println("Invalid request: update <item_number> <price>");
                    break;
                }
            case "stock":
                stock();
                break;
            case "close":
                System.out.println("The bookstore is now closed");
                System.exit(0);
                break;
            default:
                System.out.println("Invalid request... log, restock <item_number>, update <item_number> <price>, stock, close");
        }
    }

    public static void main (String [] args) {
        try {
            PropertyHandlerMapping phm = new PropertyHandlerMapping();
            XmlRpcServer xmlRpcServer;
	        WebServer server = new WebServer(8854);
            xmlRpcServer = server.getXmlRpcServer();
            phm.addHandler("sample", Server.class);
            xmlRpcServer.setHandlerMapping(phm);
            System.out.println("The bookstore is now open on port 8854");
            server.start();

            Class.forName("org.sqlite.JDBC");
            c = DriverManager.getConnection("jdbc:sqlite:test.db");
            //c.setAutoCommit(true);

            Scanner scan = new Scanner(System.in);
            while (scan.hasNext()){
                stringParser(scan.nextLine());
            }

            c.close();
    	} catch (Exception exception) {
	        System.err.println("Server: " + exception);
        }
	}

}

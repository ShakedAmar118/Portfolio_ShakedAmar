package ascii_art.exceptions;
/**
 * Exception thrown when a command is recognized but has an invalid format
 * or arguments that do not follow the expected structure.
 *
 * Used to handle incorrect usage of commands such as 'add', 'remove', 'res', etc.,
 * and to provide meaningful error messages to the user.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class IncorrectFormatException extends RuntimeException {
	/**
	 * Constructs a new IncorrectFormatException with a detailed message.
	 *
	 * @param message Description of the incorrect format or usage.
	 */
	public IncorrectFormatException(String message) {
		super(message);
	}
}

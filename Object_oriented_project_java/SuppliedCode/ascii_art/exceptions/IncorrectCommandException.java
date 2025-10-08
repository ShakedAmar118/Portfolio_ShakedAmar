package ascii_art.exceptions;

/**
 * Exception thrown when the user enters a command that does not match
 * any known instruction in the interactive shell.
 *
 * Used to notify about completely unrecognized commands that should be ignored.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class IncorrectCommandException extends RuntimeException{
	/**
	 * Constructs a new IncorrectCommandException with a detailed message.
	 *
	 * @param message Description of the invalid command entered by the user.
	 */
	public IncorrectCommandException(String message) {
		super(message);
	}
}

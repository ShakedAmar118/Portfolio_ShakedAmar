package ascii_art.exceptions;

/**
 * Exception thrown when the user attempts to change the resolution
 * beyond the allowed image boundaries (either too large or too small).
 *
 * Used to enforce valid resolution changes during user interaction.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class ExceedingBoundariesException extends RuntimeException {
	/**
	 * Constructs a new ExceedingBoundariesException with a detailed message.
	 *
	 * @param message Description of the resolution boundary violation.
	 */
	public ExceedingBoundariesException(String message) {
		super(message);
	}
}

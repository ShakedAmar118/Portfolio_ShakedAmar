package ascii_art.exceptions;

/**
 * Exception thrown when the user attempts to run the ASCII art algorithm
 * with a charset that contains fewer than two characters.
 *
 * Used to prevent execution when the character set is too small to produce valid output.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class TooSmallCharsetException extends RuntimeException{
	/**
	 * Constructs a new TooSmallCharsetException with a detailed message.
	 *
	 * @param message Description of the error regarding charset size.
	 */
	public TooSmallCharsetException(String message) {
		super(message);
	}
}

package image_char_matching;

/**
 * Enum defining the rounding mode used to match image brightness
 * to the closest character in the ASCII art algorithm.
 *
 * ABS  – Choose the closest value by absolute difference.
 * UP   – Round brightness up (ceiling).
 * DOWN – Round brightness down (floor).
 *
 * Used by SubImgCharMatcher during character selection.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public enum Round {

	/**
	 * Choose the character whose brightness has the smallest absolute
	 * difference from the target brightness.
	 */
	ABS,

	/**
	 * Always round the brightness up (ceiling) to find the closest character
	 * that is brighter or equal to the target.
	 */
	UP,

	/**
	 * Always round the brightness down (floor) to find the closest character
	 * that is darker or equal to the target.
	 */
	DOWN;
}

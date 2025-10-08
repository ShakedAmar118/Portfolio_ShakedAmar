package ascii_art;

import ascii_art.exceptions.ExceedingBoundariesException;
import ascii_art.exceptions.IncorrectCommandException;
import ascii_art.exceptions.IncorrectFormatException;
import ascii_art.exceptions.TooSmallCharsetException;
import ascii_output.AsciiOutput;
import ascii_output.ConsoleAsciiOutput;
import ascii_output.HtmlAsciiOutput;
import image.Image;
import image.ImageUtility;
import image.SubImgBrightnesses;
import image_char_matching.Round;
import image_char_matching.SubImgCharMatcher;
import java.io.IOException;

/**
 * Represents the interactive shell interface that receives user input and executes
 * commands to control the ASCII art conversion process.
 *
 * Handles the commands: add, remove, chars, res, round,
 * output, and asciiArt, as well as error handling and input validation.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class Shell {

	private static final int DEFAULT_RES = 2;
	private static final char[] DEFAULT_CHARSET = {
			'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
	};
	private static final String SPACE_STR = " ";
	private static final String EXIT_COMMAND = "exit";
	private static final int MIN_CHARS_NUM = 2;
	private static final String TOO_SMALL_CHARSET_MESSAGE = "Did not execute. Charset is too small.";
	private static final String ASCIIART_COMMAND = "asciiArt";
	private static final String ASCIIART_SPACE_COMMAND = "asciiArt ";
	private static final String CHARS_COMMAND = "chars";
	private static final String CHARS_SPACE_COMMAND = "chars ";
	private static final String ADD_SPACE_COMMAND = "add ";
	private static final String ADD_COMMAND = "add";
	private static final String INCORRECT_ADD_FORMAT_MESSAGE = "Did not add due to incorrect format.";
	private static final String INCORRECT_RES_FORMAT_MESSAGE =
			"Did not change resolution due to incorrect format.";
	private static final String SPACE_WORD = "space";
	private static final String ALL_WORD = "all";
	private static final char SPACE_CHAR = ' ';
	private static final int ASCII_UPPER_BOUND = 126;
	private static final int ASCII_LOWER_BOUND = 32;
	private static final int ADD_RANGE_LENGTH = 3;
	private static final char HYPHEN_CHAR = '-';
	private static final String ARROWS_STR = ">>> ";
	private static final String REMOVE_SPACE_COMMAND = "remove ";
	private static final String INCORRECT_REMOVE_FORMAT_MESSAGE =
			"Did not remove due to incorrect format.";
	private static final String REMOVE_COMMAND = "remove";
	private static final String RES_SPACE_COMMAND = "res ";
	private static final String RES_COMMAND = "res";
	private static final String CUR_RES_MESSAGE = "Resolution set to %d.";
	private static final String UP_WORD = "up";
	private static final String DOWN_WORD = "down";
	private static final int NUMBER_TWO = 2;
	private static final String EXCEEDING_BOUNDARIES_MESSAGE =
			"Did not change resolution due to exceeding boundaries.";
	private static final String OUTPUT_SPACE_COMMAND = "output ";
	private static final String OUTPUT_COMMAND = "output";
	private static final String INCORRECT_OUTPUT_FORMAT_MESSAGE =
			"Did not change output method due to incorrect format.";
	private static final String CONSOLE_WORD = "console";
	private static final String HTML_WORD = "html";
	private static final String OUTPUT_FILE_NAME = "out.html";
	private static final String OUTPUT_FONT = "Courier New";
	private static final String ROUND_SPACE_COMMAND = "round ";
	private static final String ROUND_COMMAND = "round";
	private static final String INCORRECT_ROUND_FORMAT_MESSAGE =
			"Did not change rounding method due to incorrect format.";
	private static final String ABS_WORD = "abs";
	private static final String INCORRECT_COMMAND_MESSAGE =
			"Did not execute due to incorrect command.";


	private boolean isResChanged;
	private Round round;
	private int resolution;
	private SubImgCharMatcher charMatcher;
	private AsciiOutput asciiOutput;
	private Image image;
	private boolean isValidCommand;
	private SubImgBrightnesses subImgBrightnesses;

	/**
	 * Constructs a new Shell instance with default settings for resolution,
	 * charset, rounding method and output mode.
	 */
	public Shell(){
		isResChanged = true;
		round = Round.ABS;
		resolution = DEFAULT_RES;
		charMatcher = new SubImgCharMatcher(DEFAULT_CHARSET);
		asciiOutput = new ConsoleAsciiOutput();
		isValidCommand = false;
	}

	/**
	 * Runs the main interactive loop, reading and executing user commands
	 * until the user enters 'exit'. Initializes the image and manages command dispatch.
	 *
	 * @param imageName The path to the image file to convert into ASCII art.
	 */
	public void run(String imageName) {
		try{
			image = new Image(imageName);
		} catch (IOException e) {
			return;
		}
		subImgBrightnesses = new SubImgBrightnesses(image, resolution);
		System.out.print(ARROWS_STR);
		String input = KeyboardInput.readLine();;
		while(!input.startsWith(EXIT_COMMAND)) {
			try{
				handleAsciiArtCommand(input);
			} catch (TooSmallCharsetException e) {
				System.out.println(e.getMessage());
			}
			handleCharsCommand(input);
			try{
				handleAddOrRemoveCommand(input);
				handleOutputCommand(input);
				handleRoundCommand(input);
			} catch (IncorrectFormatException e) {
				System.out.println(e.getMessage());
			}
			try{
				handleResCommand(input);
			} catch (IncorrectFormatException | ExceedingBoundariesException e) {
				System.out.println(e.getMessage());
			}
			try{
				if(!isValidCommand){
					throw new IncorrectCommandException(INCORRECT_COMMAND_MESSAGE);
				}
			} catch (IncorrectCommandException e){
				System.out.println(e.getMessage());
			}
			isValidCommand = false;
			System.out.print(ARROWS_STR);
			input = KeyboardInput.readLine();
		}
	}

	/**
	 * Handles the 'round' command to update the rounding mode for character matching.
	 *
	 * @param input The user input string.
	 * @throws IncorrectFormatException If the input format is invalid.
	 */
	private void handleRoundCommand(String input) throws IncorrectFormatException {
		if(input.startsWith(ROUND_SPACE_COMMAND)) {
			isValidCommand = true;
			String roundType = input.split(SPACE_STR)[1];
			if (roundType.equals(ABS_WORD)) {
				round = Round.ABS;
			} else if (roundType.equals(UP_WORD)) {
				round = Round.UP;
			} else if (roundType.equals(DOWN_WORD)) {
				round = Round.DOWN;
			} else {
				throw new IncorrectFormatException(INCORRECT_ROUND_FORMAT_MESSAGE);
			}
		} else if (input.equals(ROUND_COMMAND)) {
			isValidCommand = true;
			throw new IncorrectFormatException(INCORRECT_ROUND_FORMAT_MESSAGE);
		}
	}

	/**
	 * Handles the 'output' command to change the output destination (console or HTML).
	 *
	 * @param input The user input string.
	 * @throws IncorrectFormatException If the output mode is unrecognized.
	 */
	private void handleOutputCommand(String input) throws IncorrectFormatException {
		if(input.startsWith(OUTPUT_SPACE_COMMAND)) {
			isValidCommand = true;
			String outputType = input.split(SPACE_STR)[1];
			if (outputType.equals(CONSOLE_WORD)) {
				asciiOutput = new ConsoleAsciiOutput();
			} else if (outputType.equals(HTML_WORD)) {
				asciiOutput = new HtmlAsciiOutput(OUTPUT_FILE_NAME, OUTPUT_FONT);
			} else {
				throw new IncorrectFormatException(INCORRECT_OUTPUT_FORMAT_MESSAGE);
			}
		} else if (input.equals(OUTPUT_COMMAND)) {
			isValidCommand = true;
			throw new IncorrectFormatException(INCORRECT_OUTPUT_FORMAT_MESSAGE);
		}
	}

	/**
	 * Handles the 'res' command to increase or decrease resolution,
	 * or print the current resolution.
	 *
	 * @param input The user input string.
	 * @throws IncorrectFormatException If the format is invalid.
	 * @throws ExceedingBoundariesException If the resolution change exceeds allowed bounds.
	 */
	private void handleResCommand(String input)
			throws IncorrectFormatException, ExceedingBoundariesException{
		if (input.startsWith(RES_SPACE_COMMAND)) {
			isValidCommand = true;
			String upOrDown = input.split(SPACE_STR)[1];
			if (upOrDown.equals(UP_WORD)){
				if(resolution * NUMBER_TWO <= ImageUtility.getWidthAfterPadding(image)){
					resolution *= NUMBER_TWO;
					isResChanged = true;
					String resFormat = String.format(CUR_RES_MESSAGE, resolution);
					System.out.println(resFormat);
				} else {
					throw new ExceedingBoundariesException(EXCEEDING_BOUNDARIES_MESSAGE);
				}

			} else if (upOrDown.equals(DOWN_WORD)) {
				double minCharsInRow = Math.max(1,
						(ImageUtility.getWidthAfterPadding(image)) /
								(ImageUtility.getHeightAfterPadding(image)));
				if ((double) resolution / NUMBER_TWO >= minCharsInRow) {
					resolution /= NUMBER_TWO;
					isResChanged = true;
					String resFormat = String.format(CUR_RES_MESSAGE, resolution);
					System.out.println(resFormat);
				} else {
					throw new ExceedingBoundariesException(EXCEEDING_BOUNDARIES_MESSAGE);
				}
			}else {
				throw new IncorrectFormatException(INCORRECT_RES_FORMAT_MESSAGE);
			}
		} else if (input.equals(RES_COMMAND)) {
			isValidCommand = true;
			String resFormat = String.format(CUR_RES_MESSAGE, resolution);
			System.out.println(resFormat);
		}
	}

	/**
	 * Handles the 'add' and 'remove' commands to modify the current charset.
	 * Supports single characters, ranges (e.g., a-d), 'all', and 'space'.
	 *
	 * @param input The user input string.
	 * @throws IncorrectFormatException If the format or characters are invalid.
	 */
	private void handleAddOrRemoveCommand(String input) throws IncorrectFormatException{
		if(input.startsWith(ADD_SPACE_COMMAND) || input.startsWith(REMOVE_SPACE_COMMAND)) {
			isValidCommand = true;
			boolean isAddCommand = input.startsWith(ADD_SPACE_COMMAND);
			String whatToAdd = input.split(SPACE_STR)[1];
			if(whatToAdd.equals(SPACE_WORD)) {
				addOrRemoveFromMatcher(SPACE_CHAR, isAddCommand);
			} else if (whatToAdd.equals(ALL_WORD)) {
				for (int i = ASCII_LOWER_BOUND; i <= ASCII_UPPER_BOUND; i++) {
					addOrRemoveFromMatcher((char) i, isAddCommand);
				}
			} else if (whatToAdd.length() == 1) {
				if (!checkCharBounds(whatToAdd.charAt(0))) {
					throwAddOrRemoveException(isAddCommand);
				}
				addOrRemoveFromMatcher(whatToAdd.charAt(0), isAddCommand);
			} else if (whatToAdd.length() == ADD_RANGE_LENGTH && whatToAdd.charAt(1) == HYPHEN_CHAR) {
				char startChar = whatToAdd.charAt(0);
				char endChar = whatToAdd.charAt(ADD_RANGE_LENGTH - 1);
				if ((!checkCharBounds(startChar)) || (!checkCharBounds(endChar))) {
					throwAddOrRemoveException(isAddCommand);
				}
				if (startChar > endChar) {
					char tempChar = endChar;
					endChar = startChar;
					startChar = tempChar;
				}
				for (char c = startChar; c <= endChar; c++) {
					addOrRemoveFromMatcher(c, isAddCommand);
				}
			} else {
				throwAddOrRemoveException(isAddCommand);
			}
		} else if (input.equals(ADD_COMMAND) || input.equals(REMOVE_COMMAND)) {
			isValidCommand = true;
			throwAddOrRemoveException(input.equals(ADD_COMMAND));
		}
	}

	/**
	 * Adds or removes a single character from the charset, based on the command type.
	 *
	 * @param c The character to add or remove.
	 * @param isAddCommand True if this is an 'add' command; false if 'remove'.
	 */
	private void addOrRemoveFromMatcher(char c, boolean isAddCommand) {
		if (isAddCommand) {
			charMatcher.addChar(c);
		} else {
			charMatcher.removeChar(c);
		}
	}

	/**
	 * Throws a specific exception for add/remove command format errors.
	 *
	 * @param isAddCommand Indicates whether the exception is for 'add' or 'remove'.
	 * @throws IncorrectFormatException Always thrown with the relevant message.
	 */
	private void throwAddOrRemoveException(boolean isAddCommand) throws IncorrectFormatException {
		if (isAddCommand) {
			throw new IncorrectFormatException(INCORRECT_ADD_FORMAT_MESSAGE);
		} else {
			throw new IncorrectFormatException(INCORRECT_REMOVE_FORMAT_MESSAGE);
		}
	}

	/**
	 * Validates whether a character falls within the allowed ASCII range.
	 *
	 * @param c The character to validate.
	 * @return True if the character is within bounds, false otherwise.
	 */
	private boolean checkCharBounds(char c) {
		return (c >= ASCII_LOWER_BOUND && c <= ASCII_UPPER_BOUND);
	}

	/**
	 * Handles the 'chars' command, printing the current charset in order.
	 *
	 * @param input The user input string.
	 */
	private void handleCharsCommand(String input) {
		if(input.equals(CHARS_COMMAND) || input.startsWith(CHARS_SPACE_COMMAND)) {
			isValidCommand = true;
			System.out.println(charMatcher);
		}
	}

	/**
	 * Handles the 'asciiArt' command, executing the full conversion algorithm
	 * and outputting the result via the selected output method.
	 * If the resolution has changed, sub-image brightnesses are recomputed.
	 *
	 * @param input The user input string.
	 * @throws TooSmallCharsetException If the charset contains fewer than 2 characters.
	 */
	private void handleAsciiArtCommand(String input) throws TooSmallCharsetException {
		if(input.equals(ASCIIART_COMMAND) || input.startsWith(ASCIIART_SPACE_COMMAND)) {
			if(isResChanged){
				subImgBrightnesses.createBrightnesses(resolution);
			}
			isResChanged = false;
			isValidCommand = true;
			if(charMatcher.getCharsetSize() < MIN_CHARS_NUM) {
				throw new TooSmallCharsetException(TOO_SMALL_CHARSET_MESSAGE);
			}
			char[][] asciiArt = new AsciiArtAlgorithm(round, charMatcher,
					subImgBrightnesses.getBrightnesses()).run();
			asciiOutput.out(asciiArt);
		}


	}

	/**
	 * The main entry point for running the program from the command line.
	 *
	 * @param args Command-line arguments, expecting the image path as the first argument.
	 */
	public static void main(String[] args) {
		if (args.length == 1) {
			new Shell().run(args[0]);
		}
	}
}

# Style Mover Script

**Author:** Igor Brzezek  
**Email:** igor.brzezek@gmail.com  
**GitHub:** [github.com/igorbrzezek](https://github.com/igorbrzezek)  
**Version:** 0.6

---

## Description

This Python script processes an HTML file by moving all CSS rules from an internal `<style>` tag to inline `style` attributes on the corresponding HTML elements. It also provides several options for text transformation and reporting.

This is useful for creating standalone HTML files that are easily portable and render correctly in environments where external or embedded stylesheets are not supported (e.g., some email clients, specific web components).

---

## Features

- Moves CSS styles from a `<style>` tag to inline `style` attributes.
- Removes all `class` attributes after processing, as they are no longer needed for styling.
- Provides an option to adjust capitalization in H1-H5 headings.
- Provides an option to wrap specific content in `<pre>` tags for code blocks.
- Can report statistics on which styles were applied.
- Supports a silent "batch" mode for automated workflows, logging errors to a file.

---

## Usage

The script is run from the command line.

```bash
python style_mover_06.py -i <input_file> [options]
```

---

## Options

-   `-h`, `--help`  
    Shows the help message with a list of all options and author information.

-   `-i`, `--input <file>`  
    **(Required)** Specifies the path to the input HTML file that needs to be processed.

-   `-o`, `--output <file>`  
    **(Optional)** Specifies the path for the output HTML file. If this option is omitted, the script will create a new file by appending `_styled` to the input filename (e.g., `index.html` becomes `index_styled.html`).

-   `--capitalic`  
    Adjusts the capitalization of text within `<h1>` to `<h5>` tags. The logic is as follows:
    - The first word of the heading is always capitalized.
    - Words written in all-caps (e.g., `ACRONYMS`) are preserved.
    - Words with mixed case (e.g., `PowerPoint`) are preserved.
    - All other words are converted to lowercase.

-   `--ascii [class_name]`  
    Finds all HTML elements with the specified class and wraps their entire content within `<pre>` tags. This is useful for preserving the formatting of code blocks.
    - If a class name is provided (e.g., `--ascii my-code-class`), it will target elements with that class.
    - If used without an argument (just `--ascii`), it defaults to targeting elements with the class `code-block`.

-   `--stat`  
    Displays statistics in the console after processing. It shows a count of how many times each CSS property (e.g., `color`, `font-size`) was applied to the HTML elements.

-   `-b`, `--batch`  
    Enables batch (silent) mode. No output will be printed to the console. If any errors occur during processing, they will be logged to a file named `smover.err` in the same directory.

---

## Examples

1.  **Basic usage** (creates `my_page_styled.html`):
    ```bash
    python style_mover_06.py -i my_page.html
    ```

2.  **Specifying an output file and adjusting heading capitalization**:
    ```bash
    python style_mover_06.py -i input.html -o output.html --capitalic
    ```

3.  **Converting a specific class to a preformatted block and showing stats**:
    ```bash
    python style_mover_06.py -i document.html --ascii custom-code --stat
    ```

4.  **Running in silent mode for an automated script**:
    ```bash
    python style_mover_06.py -i template.html -b
    ```
    *(If an error occurs, check for `smover.err`)*
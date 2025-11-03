# AUTHOR: Igor Brzezek
# EMAIL: igor.brzezek@gmail.com
# GITHUB: github.com/igorbrzezek
# VERSION: 0.6
#
# Description:
# This script processes an HTML file to move CSS styles from a <style> tag
# to inline style attributes on the corresponding HTML elements.
# It offers options for text transformation, such as adjusting capitalization
# in headings and converting specific sections to preformatted text blocks.
# It can also provide statistics on the styles applied and operate in a silent
# "batch" mode, logging errors to a file.

import argparse
from bs4 import BeautifulSoup
import cssutils
import os
import logging
import sys
from collections import Counter

# --- Global variables ---
AUTHOR = "Igor Brzezek"
EMAIL = "igor.brzezek@gmail.com"
GITHUB = "github.com/igorbrzezek"
VERSION = "0.6"
error_log = []

def report_error(message):
    """Logs an error. In batch mode, it adds to a list; otherwise, prints to stderr."""
    global error_log
    error_log.append(message)

def main():
    """Main function to parse arguments and process the HTML file."""
    global error_log

    epilog_text = f"""
AUTHOR: {AUTHOR}
EMAIL: <{EMAIL}>
GITHUB: {GITHUB}
VERSION: {VERSION}
"""

    parser = argparse.ArgumentParser(
        description='Copy styles from <style> tag to inline styles in HTML elements.',
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True, help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output HTML file (optional)')
    parser.add_argument('--capitalic', action='store_true', help='Adjust capitalization in H1-H5 headings. Keeps first word capitalized, proper nouns, and acronyms.')
    parser.add_argument('--ascii', nargs='?', const='code-block', help='Wrap content of elements with a specified class (default: "code-block") in <pre> tags. E.g., --ascii my-class.')
    parser.add_argument('--stat', action='store_true', help='Show statistics of applied style properties.')
    parser.add_argument('-b', '--batch', action='store_true', help='Batch mode. Suppresses all console output and creates "smover.err" with error messages if any.')
    
    args = parser.parse_args()

    # --- Read input file ---
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        report_error(f"Error: Input file '{args.input}' not found.")
        if not args.batch:
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    style_stats = Counter()

    # --- Process <style> tag ---
    style_tag = soup.find('style')
    if not style_tag:
        if not args.batch:
            print("No <style> tag found in the HTML file. Proceeding with other operations.")
    else:
        css_text = style_tag.get_text()
        cssutils.log.setLevel(logging.CRITICAL) # Suppress all warnings
        sheet = cssutils.parseString(css_text)

        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                style_dict = {prop.name: prop.value for prop in rule.style}

                try:
                    elements = soup.select(selector)
                except Exception as e:
                    report_error(f"Error selecting elements for selector '{selector}': {e}")
                    continue

                for elem in elements:
                    existing_style = elem.get('style', '')
                    existing_dict = {}
                    if existing_style:
                        for item in existing_style.split(';'):
                            if ':' in item:
                                key, value = item.split(':', 1)
                                existing_dict[key.strip()] = value.strip()
                    
                    # Update stats before merging
                    for prop_name in style_dict.keys():
                        style_stats[prop_name] += 1

                    existing_dict.update(style_dict)
                    
                    new_style = ';'.join([f'{k}:{v}' for k, v in existing_dict.items() if k])
                    if new_style:
                        elem['style'] = new_style
        
        style_tag.decompose()

    # --- Handle --ascii option ---
    if args.ascii:
        class_to_convert = args.ascii
        if not args.batch:
            print(f"Wrapping content of elements with class '{class_to_convert}' in <pre> tags.")
        elements_to_convert = soup.find_all(attrs={'class': class_to_convert})
        for elem in elements_to_convert:
            pre_tag = soup.new_tag('pre')
            for content in list(elem.contents):
                pre_tag.append(content)
            elem.clear()
            elem.append(pre_tag)

    # --- Handle --capitalic option ---
    if args.capitalic:
        def adjust_case(text):
            words = text.split()
            if not words:
                return ""
            
            adjusted_words = []
            for i, word in enumerate(words):
                # Capitalize the first word
                if i == 0:
                    adjusted_words.append(word.capitalize())
                # Preserve words that are all uppercase
                elif word.isupper():
                    adjusted_words.append(word)
                # Preserve mixed-case words (e.g., PowerPoint)
                elif any(c.isupper() for c in word[1:]):
                    adjusted_words.append(word)
                # Lowercase all other words
                else:
                    adjusted_words.append(word.lower())
            return ' '.join(adjusted_words)

        for tag_name in ['h1', 'h2', 'h3', 'h4', 'h5']:
            for heading in soup.find_all(tag_name):
                if heading.string:
                    heading.string = adjust_case(heading.string)

    # --- Remove all class attributes ---
    for tag in soup.find_all(attrs={'class': True}):
        del tag['class']

    # --- Determine output file ---
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input)
        output_file = base + '_styled' + ext

    # --- Write output file ---
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        if not args.batch:
            print(f"Modified HTML saved to '{output_file}'")
    except Exception as e:
        report_error(f"Error writing to output file '{output_file}': {e}")

    # --- Final reporting ---
    if args.stat and not args.batch:
        print("\n--- Style Application Stats ---")
        if style_stats:
            for prop, count in sorted(style_stats.items()):
                print(f"{prop}: {count} times")
        else:
            print("No styles were applied.")
        print("-----------------------------\n")

    if args.batch and error_log:
        try:
            with open('smover.err', 'w', encoding='utf-8') as f:
                for error in error_log:
                    f.write(f"{error}\n")
        except Exception as e:
            # If we can't even write to the error file, print to stderr as a last resort
            print(f"Critical: Could not write to smover.err. Reason: {e}", file=sys.stderr)
            for error in error_log:
                print(error, file=sys.stderr)
    elif not args.batch and error_log:
        print("\n--- Errors Occurred ---", file=sys.stderr)
        for error in error_log:
            print(error, file=sys.stderr)
        print("-----------------------\n", file=sys.stderr)


if __name__ == '__main__':
    main()
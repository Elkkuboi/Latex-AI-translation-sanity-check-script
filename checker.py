#!/usr/bin/env python3
import sys
import argparse

class LatexChecker:
    def __init__(self, original_path, translated_path):
        self.original_path = original_path
        self.translated_path = translated_path
        print(f"--- Tarkistus alkaa ---")
        print(f"Alkuperäinen: {self.original_path}")
        print(f"Käännös:      {self.translated_path}")
        # Tähän tulee myöhemmin tiedoston luku

def main():
    # Luodaan komentoriviargumentit
    parser = argparse.ArgumentParser(description="Basic LaTeX Sanity Checker")
    parser.add_argument("original", help="Polku alkuperäiseen .tex tiedostoon")
    parser.add_argument("translated", help="Polku käännettyyn .tex tiedostoon")
    
    args = parser.parse_args()

    # Kutsutaan luokkaa
    checker = LatexChecker(args.original, args.translated)

if __name__ == "__main__":
    main()
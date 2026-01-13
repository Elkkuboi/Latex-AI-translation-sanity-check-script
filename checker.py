#!/usr/bin/env python3
import sys
import argparse
from colorama import Fore, Style, init

# Alustetaan värit (autoreset nollaa värin aina tulostuksen jälkeen)
init(autoreset=True)

class LatexChecker:
    def __init__(self, original_path, translated_path):
        self.original_path = original_path
        self.translated_path = translated_path
        
        print(f"{Fore.CYAN}--- Tarkistus alkaa ---")
        
        # Luetaan tiedostot heti alussa
        self.orig_content = self._read_file(original_path)
        self.trans_content = self._read_file(translated_path)

    def _read_file(self, filepath):
        """Lukee tiedoston ja käsittelee virheet, jos tiedostoa ei löydy."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"{Fore.RED}VIRHE: Tiedostoa '{filepath}' ei löytynyt.")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}VIRHE tiedoston luvussa: {e}")
            sys.exit(1)

    def check_structure(self):
        """Tarkistaa, onko aaltosulkeet { } tasapainossa."""
        print(f"[*] Tarkistetaan rakenteellista eheyttä...")
        
        open_count = self.trans_content.count('{')
        close_count = self.trans_content.count('}')
        
        if open_count != close_count:
            print(f"{Fore.RED}[!] KRIITINEN VIRHE: Aaltosulkeet eivät täsmää!")
            print(f"    Avattu {{ : {open_count} kpl")
            print(f"    Suljettu }} : {close_count} kpl")
            return False
        
        print(f"{Fore.GREEN}[+] Rakenne kunnossa.")
        return True

def main():
    parser = argparse.ArgumentParser(description="Basic LaTeX Sanity Checker")
    parser.add_argument("original", help="Polku alkuperäiseen .tex tiedostoon")
    parser.add_argument("translated", help="Polku käännettyyn .tex tiedostoon")
    
    args = parser.parse_args()

    checker = LatexChecker(args.original, args.translated)
    
    # Ajetaan tarkistus
    if checker.check_structure():
        print(f"\n{Fore.GREEN}✔ Perustarkistus läpi.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}✘ Tarkistus epäonnistui.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
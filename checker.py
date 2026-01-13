#!/usr/bin/env python3
import re
import sys
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

class LatexChecker:
    def __init__(self, original_path, translated_path):
        self.original_path = original_path
        self.translated_path = translated_path
        self.orig_content = self._read_file(original_path)
        self.trans_content = self._read_file(translated_path)

    def _read_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"{Fore.RED}VIRHE: Tiedostoa '{filepath}' ei löytynyt.")
            sys.exit(1)

    def extract_math_blocks(self, content):
        """
        Etsii ja eristää kaikki matemaattiset lohkot ja ympäristöt tekstistä.
        Palauttaa listan merkkijonoja.
        """
        # 1. Poistetaan kommentit (ettei verrata kommentoitua koodia)
        # Etsitään %-merkki, jota EI edellä kenoviiva (\)
        content_clean = re.sub(r'(?<!\\)%.*', '', content)
        
        blocks = []

        # 2. Etsitään inline math: $ ... $
        # (?<!\\) estää nappaamasta \$ merkkiä (joka on dollarimerkki tekstissä)
        blocks.extend(re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', content_clean, re.DOTALL))

        # 3. Etsitään display math: \[ ... \]
        blocks.extend(re.findall(r'\\\[(.*?)\\\]', content_clean, re.DOTALL))

        # 4. Etsitään kaikki LaTeX-ympäristöt: \begin{...} ... \end{...}
        # Tämä nappaa equation, align, itemize, jne.
        # Jos käännöksessä equation muuttuu aligniksi tai katoaa, tämä huomaa sen.
        # Regex nappaa sisällön talteen.
        blocks.extend(re.findall(r'\\begin\{.*?\}(.*?)\\end\{.*?\}', content_clean, re.DOTALL))
        
        # Siivotaan turhat välilyönnit ja rivinvaihdot vertailua varten.
        # Esim "x + y" on sama kuin "x+y"
        cleaned_blocks = [b.strip().replace(" ", "").replace("\n", "") for b in blocks]
        
        return cleaned_blocks

    def compare_math(self):
        print(f"{Fore.CYAN}[*] Verrataan matematiikkaa ja ympäristöjä kahden tiedoston välillä...")
        
        orig_blocks = self.extract_math_blocks(self.orig_content)
        trans_blocks = self.extract_math_blocks(self.trans_content)
        
        errors = 0
        
        # TARKISTUS 1: Määrien vertailu
        if len(orig_blocks) != len(trans_blocks):
            print(f"{Fore.RED}[!] KRITITINEN VIRHE: Lohkojen määrä ei täsmää!")
            print(f"    Alkuperäinen tiedosto: {len(orig_blocks)} kpl")
            print(f"    Käännetty tiedosto:    {len(trans_blocks)} kpl")
            print(f"    {Fore.YELLOW}-> Jossain on kadonnut tai ilmestynyt ylimääräinen kaava tai ympäristö.")
            # Ei lopeteta tähän, vaan yritetään näyttää missä ero on
            errors += 1
            
        # TARKISTUS 2: Sisällön vertailu
        # Verrataan niin pitkälle kuin lyhyempi lista riittää
        limit = min(len(orig_blocks), len(trans_blocks))
        
        for i in range(limit):
            if orig_blocks[i] != trans_blocks[i]:
                print(f"{Fore.YELLOW}[x] Eroavuus lohkossa #{i+1}:")
                # Näytetään vain 50 ekaa merkkiä ettei floodata ruutua
                print(f"    Orig:  {orig_blocks[i][:60]}...")
                print(f"    Trans: {trans_blocks[i][:60]}...")
                errors += 1

        if errors == 0:
            print(f"{Fore.GREEN}[+] Kaikki {len(orig_blocks)} matemaattista lohkoa/ympäristöä ovat identtiset.")
            return True
        else:
            print(f"{Fore.RED}[-] Löydettiin yhteensä {errors} virhettä vertailussa.")
            return False

def main():
    parser = argparse.ArgumentParser(description="LaTeX Translation Comparator")
    parser.add_argument("original", help="Polku alkuperäiseen .tex tiedostoon")
    parser.add_argument("translated", help="Polku käännettyyn .tex tiedostoon")
    
    args = parser.parse_args()

    checker = LatexChecker(args.original, args.translated)
    
    if checker.compare_math():
        print(f"\n{Fore.GREEN}✔ VERTAILU OK: Tiedostot vastaavat matemaattisesti toisiaan.{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}✘ VERTAILU EPÄONNISTUI.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
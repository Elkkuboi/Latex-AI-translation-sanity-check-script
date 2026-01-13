#!/usr/bin/env python3
import re
import sys
import argparse
import difflib
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

    def normalize_math(self, math_str):
        # 1. Poistetaan välilyönnit ja rivinvaihdot
        s = math_str.strip().replace(" ", "").replace("\n", "")
        
        # 2. Neutralisoidaan \text{...} ja \mbox{...} sisällöt
        s = re.sub(r'\\text\{.*?\}', r'\\text{TEXT}', s)
        s = re.sub(r'\\mbox\{.*?\}', r'\\mbox{TEXT}', s)
        
        # 3. UUSI: Poistetaan pisteet ja pilkut vain kaavan LOPUSTA.
        # Tämä korjaa tilanteen, jossa piste on siirretty $...$ ulkopuolelle.
        s = s.rstrip('.,')
        
        return s

    def extract_math_blocks(self, content):
        content_clean = re.sub(r'(?<!\\)%.*', '', content)
        blocks = []

        # 1. Inline math $...$
        blocks.extend(re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', content_clean, re.DOTALL))

        # 2. Display math \[...\]
        blocks.extend(re.findall(r'\\\[(.*?)\\\]', content_clean, re.DOTALL))

        # 3. VAIN tietyt matematiikka-ympäristöt (Whitelist)
        # Emme enää käytä ".*?", joka nappaa myös definition/theorem/document -ympäristöt.
        # Listataan ne, jotka sisältävät vain kaavoja.
        math_envs = [
            r'equation', r'equation\*',
            r'align', r'align\*',
            r'gather', r'gather\*',
            r'split',
            r'multline', r'multline\*',
            r'alignat', r'alignat\*'
        ]
        
        # Rakennetaan regex, joka etsii vain näitä.
        # Esim: \\begin\{(equation|align)\}(.*?)\\end\{\1\}
        env_pattern = r'\\begin\{(' + '|'.join(math_envs) + r')\}(.*?)\\end\{\1\}'
        
        # findall palauttaa tuplen (ympäristön_nimi, sisältö), me haluamme vain sisällön [1]
        matches = re.findall(env_pattern, content_clean, re.DOTALL)
        blocks.extend([m[1] for m in matches])
        
        return [self.normalize_math(b) for b in blocks]

    def compare_math(self):
        print(f"{Fore.CYAN}[*] Analysoidaan matematiikkaa (vain kaavat ja math-ympäristöt)...")
        
        orig_blocks = self.extract_math_blocks(self.orig_content)
        trans_blocks = self.extract_math_blocks(self.trans_content)
        
        matcher = difflib.SequenceMatcher(None, orig_blocks, trans_blocks)
        errors = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            
            if tag == 'replace':
                for k in range(i2 - i1):
                    print(f"{Fore.RED}[x] MUUTOS KAAVASSA:")
                    print(f"    Orig:  {orig_blocks[i1+k][:80]}")
                    print(f"    Trans: {trans_blocks[j1+k][:80]}")
                    errors += 1
            elif tag == 'delete':
                for k in range(i1, i2):
                    print(f"{Fore.YELLOW}[-] PUUTTUU KÄÄNNÖKSESTÄ:")
                    print(f"    '{orig_blocks[k][:60]}'")
                    errors += 1
            elif tag == 'insert':
                for k in range(j1, j2):
                    print(f"{Fore.YELLOW}[+] YLIMÄÄRÄINEN KÄÄNNÖKSESSÄ:")
                    print(f"    '{trans_blocks[k][:60]}'")
                    errors += 1

        print(f"\nAnalyysi valmis.")
        if errors == 0:
            print(f"{Fore.GREEN}✔ Matematiikka täsmää.")
            return True
        else:
            print(f"{Fore.RED}✘ Löydettiin {errors} poikkeamaa.")
            return False

def main():
    parser = argparse.ArgumentParser(description="LaTeX Translation Comparator (Smart Diff)")
    parser.add_argument("original", help="Polku alkuperäiseen .tex tiedostoon")
    parser.add_argument("translated", help="Polku käännettyyn .tex tiedostoon")
    
    args = parser.parse_args()
    checker = LatexChecker(args.original, args.translated)
    
    if checker.compare_math():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
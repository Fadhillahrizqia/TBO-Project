class CFG:
    def __init__(self, rules):
        if not rules:
            raise ValueError("rules must be a non-empty dict")
        self.rules = rules
        self.start = next(iter(rules))  # simbol pertama jadi start symbol

    def parse(self, tokens):
        result_positions = self._derive(self.start, tokens, 0)

        # accepted jika ada posisi hasil yang mencapai akhir token
        return len(tokens) in result_positions

    def _derive(self, symbol, tokens, pos):
        """
        Mengembalikan set posisi setelah symbol diproses.
        Jika kosong → gagal.
        """
        results = set()

        # Jika terminal:
        if symbol not in self.rules:
            if pos < len(tokens) and tokens[pos] == symbol:
                return {pos + 1}
            return set()

        # Jika nonterminal:
        for production in self.rules[symbol]:
            positions = {pos}  # mulai dari posisi awal

            for sym in production:
                new_positions = set()
                for p in positions:
                    out = self._derive(sym, tokens, p)
                    new_positions |= out
                positions = new_positions

                if not positions:
                    break  # produksi gagal, coba produksi lain

            results |= positions

        return results

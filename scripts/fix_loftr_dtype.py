from pathlib import Path

p = Path("src/parallex/matching/loftr.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
'''        self.model = LoFTR(
            pretrained=self.pretrained
        ).eval()
''',
'''        self.model = LoFTR(
            pretrained=self.pretrained
        ).eval().float()
'''
)

s = s.replace(
'''        tensor_a = tensor_a.to(device)
        tensor_b = tensor_b.to(device)
''',
'''        tensor_a = tensor_a.to(
            device=device,
            dtype=torch.float32
        )
        tensor_b = tensor_b.to(
            device=device,
            dtype=torch.float32
        )
'''
)

p.write_text(s, encoding="utf-8")

print("LoFTR dtype fix applied.")

from dataclasses import dataclass, field

@dataclass
class AppMetaData:
    name: str = 'Corpusaige'
    version: str = '0.10.0'
    description: str = '''Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis through deep exploration and understanding of comprehensive document sets and source code.'''
    authors: list = field(default_factory=lambda: ['Iwan van der Kleijn <iwanvanderkleijn@gmail.com>'])
    license: str = 'MIT'

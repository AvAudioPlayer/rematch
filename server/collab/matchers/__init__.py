from .matcher import Matcher
from .hash_matcher import HashMatcher
from .euclidean_matcher import EuclideanDictionaryMatcher
from .instruction_hash import InstructionHashMatcher
from .identity_hash import IdentityHashMatcher
from .assembly_hash import AssemblyHashMatcher
from .mnemonic_hash import MnemonicHashMatcher
from .name_hash import NameHashMatcher
from .mnemonic_euclidean import MnemonicEuclideanMatcher
from .dictionary_matcher import DictionaryMatcher


matchers_list = [InstructionHashMatcher, IdentityHashMatcher, NameHashMatcher,
                 AssemblyHashMatcher, MnemonicHashMatcher,
                 MnemonicEuclideanMatcher]


def get_matcher(matcher):
  for matcher_cls in matchers_list:
    if matcher_cls.matcher_type == matcher:
      return matcher_cls

  matcher_types = [s.matcher_type for s in matchers_list]
  raise ValueError("Couldn't find requested matcher {} out of available "
                   "matchers: {}".format(matcher, matcher_types))


__all__ = ['Matcher', 'HashMatcher', 'EuclideanDictionaryMatcher',
           'InstructionHashMatcher', 'IdentityHashMatcher',
           'AssemblyHashMatcher', 'MnemonicHashMatcher', 'NameHashMatcher',
           'MnemonicEuclideanMatcher', 'DictionaryMatcher', 'matchers_list',
           'get_matcher']

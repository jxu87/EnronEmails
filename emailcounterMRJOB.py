from mrjob.job import MRJob

import re

class MRWordFrequencyCount(MRJob):

	def mapper(self, _, line):
		fromRE = re.compile("^From: ([^<\[]*)")
		if fromRE.match(line):
			match = fromRE.search(line).group(1).strip()
			if match is not None:
				yield match, 1

	def reducer(self, key, values):
		yield key, sum(values)


if __name__ == '__main__':
    MRWordFrequencyCount.run()

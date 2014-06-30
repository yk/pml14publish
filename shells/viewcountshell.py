import core.pml as pml


class ViewCountShell(pml.SubmodularShell):
    def configTypes(self):
        return dict(truncation_thr=float)

    def filter(self, datum):
        return 'views' in datum.meta()

    def prepare(self, data):
        self.totalViewCount = self.getViewCount(data)

    def evaluate(self, subset):
        count = self.getViewCount(subset)
        return min(count, self._truncation_thr * self.totalViewCount)

    def getViewCount(self, data):
        return sum([datum.meta()['views'] for datum in data])

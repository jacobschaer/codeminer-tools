from .entity import RepositoryEntity

class RepositoryFile(RepositoryEntity):
    def read(self):
        return self.repository.get_file_contents(
            self.path, revision=self.revision).read()

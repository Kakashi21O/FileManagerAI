from models.folder_node import FolderNode


class TreeBuilder:

    def build(self, root: FolderNode) -> FolderNode:
        self._validate(root)
        return root

    def _validate(self, folder: FolderNode) -> None:
        for file in folder.files:
            if file.path.parent != folder.path:
                raise ValueError(
                    f"File has incorrect parent: {file.path}"
                )

        for child in folder.children:
            if child.path.parent != folder.path:
                raise ValueError(
                    f"Folder has incorrect parent: {child.path}"
                )

            self._validate(child)

    def traverse(self, folder: FolderNode):
        yield folder

        for file in folder.files:
            yield file

        for child in folder.children:
            yield from self.traverse(child)
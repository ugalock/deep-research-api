import abc

class TextSplitterParams:
    """
    Parameters for controlling text chunk size and overlap.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Cannot have chunkOverlap >= chunkSize")

class TextSplitter(TextSplitterParams, metaclass=abc.ABCMeta):
    """
    Abstract base class for splitting text into chunks.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)

    @abc.abstractmethod
    def split_text(self, text: str) -> list[str]:
        """
        Splits a single string into chunks. Must be implemented by subclasses.
        """
        pass

    def create_documents(self, texts: list[str]) -> list[str]:
        """
        Splits multiple strings and returns them all as a list of chunks.
        """
        documents: list[str] = []
        for txt in texts:
            chunks = self.split_text(txt)
            documents.extend(chunks)
        return documents

    def split_documents(self, documents: list[str]) -> list[str]:
        """
        Convenience function that calls create_documents.
        """
        return self.create_documents(documents)

    def _join_docs(self, docs: list[str], separator: str) -> str | None:
        """
        Joins a list of strings with a separator, returning None if empty.
        """
        joined = separator.join(docs).strip()
        return None if joined == '' else joined

    def merge_splits(self, splits: list[str], separator: str) -> list[str]:
        """
        Merges consecutive splits into chunks based on chunk_size, with overlap checking.
        """
        docs: list[str] = []
        current_doc: list[str] = []
        total_len = 0

        for split_text in splits:
            chunk_len = len(split_text)
            if total_len + chunk_len >= self.chunk_size:
                if total_len > self.chunk_size:
                    # This is a warning in the TS version; We'll just note it here
                    # print(f"Created a chunk of size {total_len}, which is longer than {self.chunk_size}")
                    pass

                if current_doc:
                    doc = self._join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)

                    # Pop from current_doc while total_len is above chunkOverlap
                    while (total_len > self.chunk_overlap or 
                           (total_len + chunk_len > self.chunk_size and total_len > 0)):
                        item_len = len(current_doc[0])
                        total_len -= item_len
                        current_doc.pop(0)

            current_doc.append(split_text)
            total_len += chunk_len

        # Final chunk
        final_doc = self._join_docs(current_doc, separator)
        if final_doc is not None:
            docs.append(final_doc)

        return docs


class RecursiveCharacterTextSplitter(TextSplitter):
    """
    Splits text by a prioritized list of separators, recursively merging or further splitting text.
    """
    def __init__(self,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 separators: list[str] | None = None):
        super().__init__(chunk_size, chunk_overlap)
        if separators is None:
            separators = ['\n\n', '\n', '.', ',', '>', '<', ' ', '']
        self.separators = separators

    def split_text(self, text: str) -> list[str]:
        """
        Recursively splits the text based on the first separator found.
        If no separators match, splits by character. Then merges, 
        and if a chunk is still too large, calls split_text again.
        """
        final_chunks: list[str] = []
        if not text:
            return final_chunks

        # Get the first separator that exists in text; if none do, use the last one
        separator_in_use: str = self.separators[-1]
        for sep in self.separators:
            if sep == "":
                separator_in_use = sep
                break
            if sep in text:
                separator_in_use = sep
                break

        # Now split the text on that separator
        if separator_in_use:
            splits = text.split(separator_in_use)
        else:
            splits = list(text)

        # Merge them into chunks respecting chunk_size
        good_splits: list[str] = []
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                # handle the portion we have so far
                if good_splits:
                    merged = self.merge_splits(good_splits, separator_in_use)
                    final_chunks.extend(merged)
                    good_splits = []
                # recursively split the large segment
                sub_splits = self.split_text(s)
                final_chunks.extend(sub_splits)

        # handle leftover
        if good_splits:
            merged = self.merge_splits(good_splits, separator_in_use)
            final_chunks.extend(merged)

        return final_chunks
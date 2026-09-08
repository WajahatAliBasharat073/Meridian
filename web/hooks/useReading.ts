import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createReadingBook, getReadingBooks, logReadingSession, updateReadingBook } from "@/lib/api";
import type { ReadingBookCreateInput, ReadingBookUpdateInput, ReadingSessionCreateInput } from "@/lib/types";

export const READING_BOOKS_QUERY_KEY = ["reading-books"] as const;

export function useReadingBooks() {
  return useQuery({
    queryKey: READING_BOOKS_QUERY_KEY,
    queryFn: () => getReadingBooks(),
  });
}

export function useCreateReadingBook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ReadingBookCreateInput) => createReadingBook(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: READING_BOOKS_QUERY_KEY }),
  });
}

export function useUpdateReadingBook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookId, input }: { bookId: number; input: ReadingBookUpdateInput }) =>
      updateReadingBook(bookId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: READING_BOOKS_QUERY_KEY }),
  });
}

export function useLogReadingSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookId, input }: { bookId: number; input: ReadingSessionCreateInput }) =>
      logReadingSession(bookId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: READING_BOOKS_QUERY_KEY }),
  });
}

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addReadingQuote,
  createReadingBook,
  deleteReadingBook,
  deleteReadingQuote,
  getReadingBooks,
  getReadingStats,
  logReadingSession,
  updateReadingBook,
} from "@/lib/api";
import type {
  ReadingBookCreateInput,
  ReadingBookFilters,
  ReadingBookUpdateInput,
  ReadingQuoteCreateInput,
  ReadingSessionCreateInput,
} from "@/lib/types";

export const READING_BOOKS_QUERY_KEY = ["reading-books"] as const;
const READING_STATS_QUERY_KEY = ["reading-stats"] as const;

export function useReadingBooks(filters: ReadingBookFilters = {}) {
  return useQuery({
    queryKey: [...READING_BOOKS_QUERY_KEY, filters],
    queryFn: () => getReadingBooks(filters),
  });
}

export function useReadingStats() {
  return useQuery({
    queryKey: READING_STATS_QUERY_KEY,
    queryFn: getReadingStats,
  });
}

function useInvalidateReading() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: READING_BOOKS_QUERY_KEY });
    queryClient.invalidateQueries({ queryKey: READING_STATS_QUERY_KEY });
  };
}

export function useCreateReadingBook() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: (input: ReadingBookCreateInput) => createReadingBook(input),
    onSuccess: invalidate,
  });
}

export function useUpdateReadingBook() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: ({ bookId, input }: { bookId: number; input: ReadingBookUpdateInput }) =>
      updateReadingBook(bookId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteReadingBook() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: (bookId: number) => deleteReadingBook(bookId),
    onSuccess: invalidate,
  });
}

export function useLogReadingSession() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: ({ bookId, input }: { bookId: number; input: ReadingSessionCreateInput }) =>
      logReadingSession(bookId, input),
    onSuccess: invalidate,
  });
}

export function useAddReadingQuote() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: ({ bookId, input }: { bookId: number; input: ReadingQuoteCreateInput }) =>
      addReadingQuote(bookId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteReadingQuote() {
  const invalidate = useInvalidateReading();
  return useMutation({
    mutationFn: ({ bookId, quoteIndex }: { bookId: number; quoteIndex: number }) =>
      deleteReadingQuote(bookId, quoteIndex),
    onSuccess: invalidate,
  });
}

import { useCallback, useState } from "react";

export function useApiAction<TArgs extends unknown[], TResult>(
  action: (...args: TArgs) => Promise<TResult>,
) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const execute = useCallback(
    async (...args: TArgs): Promise<TResult | null> => {
      setIsLoading(true);
      setError("");

      try {
        return await action(...args);
      } catch (actionError) {
        setError(
          actionError instanceof Error
            ? actionError.message
            : "The request could not be completed.",
        );
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [action],
  );

  return {
    execute,
    isLoading,
    error,
    clearError: () => setError(""),
  };
}

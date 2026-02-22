import { useCallback, useSyncExternalStore } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth";
import { tokenStore } from "@/services/api";
import type { LoginRequest } from "@/types";

const tokenListeners = new Set<() => void>();
function notifyTokenChange() {
  tokenListeners.forEach((l) => l());
}

function useHasTokens(): boolean {
  const subscribe = useCallback((cb: () => void) => {
    tokenListeners.add(cb);
    return () => tokenListeners.delete(cb);
  }, []);
  return useSyncExternalStore(subscribe, () => !!tokenStore.get());
}

export function useAuth() {
  const hasTokens = useHasTokens();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authService.me,
    enabled: hasTokens,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const isAuthenticated = !!user;
  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";

  return { user, isLoading: hasTokens && isLoading, isAuthenticated, isAdmin, error };
}

export function useLogin() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: LoginRequest) => authService.login(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["auth", "me"], data.user);
      notifyTokenChange();
      navigate("/dashboard");
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      queryClient.clear();
      notifyTokenChange();
      navigate("/login");
    },
  });
}

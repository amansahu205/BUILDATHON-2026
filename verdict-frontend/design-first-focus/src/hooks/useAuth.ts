import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth";
import { tokenStore } from "@/services/api";
import type { LoginRequest } from "@/types";

export function useAuth() {
  const queryClient = useQueryClient();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authService.me,
    enabled: !!tokenStore.get(),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const isAuthenticated = !!user;
  const isAdmin = user?.role === "admin";

  return { user, isLoading, isAuthenticated, isAdmin, error };
}

export function useLogin() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: LoginRequest) => authService.login(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth"] });
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
      navigate("/login");
    },
  });
}

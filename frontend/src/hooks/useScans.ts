import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, CreateScanParams } from '../api/client';
import { ScanFilter } from '../types';

export const SCAN_KEYS = {
  all: ['scans'] as const,
  lists: () => [...SCAN_KEYS.all, 'list'] as const,
  list: (filter?: ScanFilter) => [...SCAN_KEYS.lists(), filter] as const,
  details: () => [...SCAN_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...SCAN_KEYS.details(), id] as const,
  stats: () => ['scans', 'stats'] as const,
};

export function useStats() {
  return useQuery({
    queryKey: SCAN_KEYS.stats(),
    queryFn: () => apiClient.getStats(),
    staleTime: 2000,
  });
}

export function useScans(filter?: ScanFilter) {
  return useQuery({
    queryKey: SCAN_KEYS.list(filter),
    queryFn: () => apiClient.listScans(filter),
    staleTime: 1000,
  });
}

export function useScan(id: string, enabled = true) {
  return useQuery({
    queryKey: SCAN_KEYS.detail(id),
    queryFn: () => apiClient.getScan(id),
    enabled: Boolean(id) && enabled,
    staleTime: 0, // Always consider scan detail fresh
    refetchInterval: (query) => {
      const scan = query.state.data;
      // If data is not yet loaded, or if scan is queued or running, poll every 500ms
      if (!scan || scan.status === 'queued' || scan.status === 'running') {
        return 500;
      }
      // Stop polling immediately once terminal state (completed / failed / partial) is reached
      return false;
    },
    refetchIntervalInBackground: true,
  });
}

export function useCreateScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: CreateScanParams) => apiClient.createScan(params),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.stats() });
    },
  });
}

export function useDeleteScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteScan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.stats() });
    },
  });
}

export function useDeleteAllScans() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.deleteAllScans(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.stats() });
    },
  });
}

export function useResetSampleScans() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.resetSampleScans(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.stats() });
    },
  });
}

export function useRetryStep() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, stepKey }: { id: string; stepKey: string }) =>
      apiClient.retryScanStep(id, stepKey),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: SCAN_KEYS.all });
    },
  });
}

import create from 'zustand';

// TODO: Implement the analysis store
const useAnalysisStore = create((set) => ({
    analysisResults: {},
    setAnalysisResults: (results) => set({ analysisResults: results }),
    isLoading: false,
    setIsLoading: (loading) => set({ isLoading: loading }),
    error: null,
    setError: (error) => set({ error: error }),
}));

export default useAnalysisStore;

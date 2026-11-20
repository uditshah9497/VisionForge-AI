import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { OverviewView } from './components/views/OverviewView';
import { SyntheticStudioView } from './components/views/SyntheticStudioView';
import { QuestionFactoryView } from './components/views/QuestionFactoryView';
import { GroundTruthView } from './components/views/GroundTruthView';
import { ValidationCenterView } from './components/views/ValidationCenterView';
import { ModelArenaView } from './components/views/ModelArenaView';
import { BlindSpotView } from './components/views/BlindSpotView';
import { AnalyticsView } from './components/views/AnalyticsView';
import { ReportsView } from './components/views/ReportsView';
import { SettingsView } from './components/views/SettingsView';
import { Dataset, AnalyticsOverview } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [selectedDataset, setSelectedDataset] = useState<any>(null);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);

  const loadGlobalData = async () => {
    try {
      const [dList, aData] = await Promise.all([
        api.getDatasets(),
        api.getAnalyticsOverview()
      ]);
      setDatasets(dList);
      setAnalytics(aData);

      if (dList.length > 0) {
        const activeId = selectedDatasetId || dList[0].id;
        setSelectedDatasetId(activeId);
        const detailed = await api.getDataset(activeId);
        setSelectedDataset(detailed);
      }
    } catch (err) {
      console.error('Failed to load global benchmark data', err);
    }
  };

  useEffect(() => {
    loadGlobalData();
  }, []);

  const handleSelectDatasetId = async (id: string) => {
    setSelectedDatasetId(id);
    try {
      const detailed = await api.getDataset(id);
      setSelectedDataset(detailed);
    } catch (err) {
      console.error(err);
    }
  };

  const getTabTitle = () => {
    switch (currentTab) {
      case 'overview': return 'Overview Dashboard';
      case 'studio': return 'Synthetic Studio';
      case 'questions': return 'Question Factory';
      case 'ground_truth': return 'Ground Truth Engine';
      case 'validation': return 'Validation Center';
      case 'arena': return 'Model Arena';
      case 'blind_spot': return 'Visual Blind Spot Discovery';
      case 'analytics': return 'Benchmark Analytics';
      case 'reports': return 'Certified Reports';
      case 'settings': return 'System Settings';
    }
  };

  return (
    <div className="flex h-screen bg-[#080C14] text-slate-100 overflow-hidden font-sans">
      {/* Sleek Enterprise Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        datasetCount={datasets.length}
        evalCount={analytics?.evaluation_runs_count}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar
          currentTabName={getTabTitle()}
          datasets={datasets}
          selectedDatasetId={selectedDatasetId}
          onSelectDatasetId={handleSelectDatasetId}
        />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            {currentTab === 'overview' && (
              <OverviewView
                analytics={analytics}
                datasets={datasets}
                onNavigate={setCurrentTab}
              />
            )}
            {currentTab === 'studio' && (
              <SyntheticStudioView
                datasets={datasets}
                selectedDataset={selectedDataset}
                onRefresh={loadGlobalData}
              />
            )}
            {currentTab === 'questions' && <QuestionFactoryView />}
            {currentTab === 'ground_truth' && (
              <GroundTruthView selectedDataset={selectedDataset} />
            )}
            {currentTab === 'validation' && <ValidationCenterView />}
            {currentTab === 'arena' && (
              <ModelArenaView
                datasets={datasets}
                selectedDatasetId={selectedDatasetId}
              />
            )}
            {currentTab === 'blind_spot' && <BlindSpotView />}
            {currentTab === 'analytics' && <AnalyticsView analytics={analytics} />}
            {currentTab === 'reports' && <ReportsView />}
            {currentTab === 'settings' && <SettingsView />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;

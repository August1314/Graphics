import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Rendering
  render: (shapes: any[]) => ipcRenderer.invoke('render', shapes),

  // Document operations
  saveDocument: (filepath: string, data: any) =>
    ipcRenderer.invoke('save-document', filepath, data),
  loadDocument: (filepath: string) =>
    ipcRenderer.invoke('load-document', filepath),

  // Menu events
  onMenuNew: (callback: () => void) => ipcRenderer.on('menu-new', callback),
  onMenuOpen: (callback: (filepath: string) => void) =>
    ipcRenderer.on('menu-open', (event, filepath) => callback(filepath)),
  onMenuSave: (callback: () => void) => ipcRenderer.on('menu-save', callback),
  onMenuSaveAs: (callback: (filepath: string) => void) =>
    ipcRenderer.on('menu-save-as', (event, filepath) => callback(filepath)),
  onMenuExportPng: (callback: () => void) =>
    ipcRenderer.on('menu-export-png', callback),
  onMenuUndo: (callback: () => void) => ipcRenderer.on('menu-undo', callback),
  onMenuRedo: (callback: () => void) => ipcRenderer.on('menu-redo', callback),
  onMenuResetZoom: (callback: () => void) =>
    ipcRenderer.on('menu-reset-zoom', callback),
  onMenuZoomIn: (callback: () => void) =>
    ipcRenderer.on('menu-zoom-in', callback),
  onMenuZoomOut: (callback: () => void) =>
    ipcRenderer.on('menu-zoom-out', callback),
});

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: {
      render: (shapes: any[]) => Promise<any>;
      saveDocument: (filepath: string, data: any) => Promise<any>;
      loadDocument: (filepath: string) => Promise<any>;
      onMenuNew: (callback: () => void) => void;
      onMenuOpen: (callback: (filepath: string) => void) => void;
      onMenuSave: (callback: () => void) => void;
      onMenuSaveAs: (callback: (filepath: string) => void) => void;
      onMenuExportPng: (callback: () => void) => void;
      onMenuUndo: (callback: () => void) => void;
      onMenuRedo: (callback: () => void) => void;
      onMenuResetZoom: (callback: () => void) => void;
      onMenuZoomIn: (callback: () => void) => void;
      onMenuZoomOut: (callback: () => void) => void;
    };
  }
}

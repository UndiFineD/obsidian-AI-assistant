// Mock Obsidian API for Jest testing

class MockApp {
  constructor() {
    this.workspace = new MockWorkspace();
  }
}

class MockWorkspace {
  constructor() {
    this.leaves = [];
  }

  detachLeavesOfType(viewType) {
    this.leaves = this.leaves.filter(leaf => leaf.viewType !== viewType);
  }

  getRightLeaf(split) {
    return new MockLeaf();
  }

  getLeavesOfType(viewType) {
    return this.leaves.filter(leaf => leaf.viewType === viewType);
  }

  revealLeaf(leaf) {
    // Mock implementation
  }
}

class MockLeaf {
  constructor() {
    this.viewType = null;
  }

  async setViewState(state) {
    this.viewType = state.type;
  }
}

class MockPlugin {
  constructor() {
    this.app = new MockApp();
  }

  registerView(viewType, factory) {
    // Mock implementation
  }

  addCommand(command) {
    // Mock implementation
  }

  addRibbonIcon(icon, title, callback) {
    return { remove: () => {} };
  }

  addSettingTab(tab) {
    // Mock implementation
  }

  async loadData() {
    return {};
  }

  async saveData(data) {
    // Mock implementation
  }
}

class MockItemView {
  constructor(leaf) {
    this.leaf = leaf;
    this.containerEl = {
      empty: () => {},
      createEl: (tag, attrs) => new MockElement(tag, attrs)
    };
  }
}

class MockElement {
  constructor(tag, attrs = {}) {
    this.tag = tag;
    this.attrs = attrs;
    this.children = [];
  }

  createEl(tag, attrs) {
    const child = new MockElement(tag, attrs);
    this.children.push(child);
    return child;
  }

  addEventListener(event, handler) {
    // Mock implementation
  }
}

class MockNotice {
  constructor(message) {
    this.message = message;
  }
}

class MockModal {
  constructor(app) {
    this.app = app;
  }

  open() {}
  close() {}
}

class MockPluginSettingTab {
  constructor(app, plugin) {
    this.app = app;
    this.plugin = plugin;
    this.containerEl = new MockElement('div');
  }
}

class MockSetting {
  constructor(containerEl) {
    this.containerEl = containerEl;
  }

  setName(name) {
    this.name = name;
    return this;
  }

  setDesc(desc) {
    this.desc = desc;
    return this;
  }

  addText(callback) {
    const textComponent = {
      setValue: (value) => textComponent,
      onChange: (callback) => textComponent
    };
    if (callback) callback(textComponent);
    return this;
  }

  addToggle(callback) {
    const toggleComponent = {
      setValue: (value) => toggleComponent,
      onChange: (callback) => toggleComponent
    };
    if (callback) callback(toggleComponent);
    return this;
  }

  addDropdown(callback) {
    const dropdownComponent = {
      addOption: (value, display) => dropdownComponent,
      setValue: (value) => dropdownComponent,
      onChange: (callback) => dropdownComponent
    };
    if (callback) callback(dropdownComponent);
    return this;
  }
}

module.exports = {
  App: MockApp,
  Plugin: MockPlugin,
  ItemView: MockItemView,
  Notice: MockNotice,
  Modal: MockModal,
  PluginSettingTab: MockPluginSettingTab,
  Setting: MockSetting,
  WorkspaceLeaf: MockLeaf,
  TFile: class MockTFile {},
  ButtonComponent: class MockButtonComponent {}
};
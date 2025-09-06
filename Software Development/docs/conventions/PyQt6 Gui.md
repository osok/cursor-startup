# PyQt6 GUI Conventions

## Project Structure
```
src/app/
├── models/              # Data models & business logic
├── views/               # GUI windows & widgets
│   ├── windows/         # Main windows
│   ├── widgets/         # Custom widgets
│   └── dialogs/         # Modal dialogs
├── controllers/         # Event handlers & business logic
├── resources/           # UI files, icons, stylesheets
└── utils/               # GUI utilities & helpers
```

## Architecture Pattern - MVC
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MODEL       │    │   CONTROLLER    │    │      VIEW       │
│                 │    │                 │    │                 │
│ - Data Classes  │◄──►│ - Event Handler │◄──►│ - Windows       │
│ - Repositories  │    │ - Business Logic│    │ - Widgets       │
│ - Validation    │    │ - State Mgmt    │    │ - Dialogs       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Hierarchy
```
QApplication
├── MainWindow (QMainWindow)
│   ├── MenuBar
│   ├── ToolBar
│   ├── StatusBar
│   └── CentralWidget
│       ├── ControlPanel (Custom Widget)
│       └── ContentArea (Custom Widget)
│           ├── ListView/ScrollArea
│           └── ItemWidgets (Custom)
└── Dialogs (QDialog)
    ├── SettingsDialog
    └── AboutDialog
```

## Threading Architecture
```
Main Thread (GUI)
├── UI Updates Only
├── Event Handling
└── Signal/Slot Connections

Worker Threads
├── Background Processing
├── File I/O Operations
├── Network Requests
└── Heavy Computations

Communication: Qt Signals/Slots (Thread-Safe)
```

## Application Lifecycle
1. **Initialization**: Create QApplication, load settings, setup logging
2. **UI Setup**: Initialize main window, connect signals, restore state
3. **Event Loop**: Handle user interactions, process events
4. **Cleanup**: Save state, disconnect signals, cleanup resources
5. **Shutdown**: Proper thread termination, resource deallocation

## Window Management
- **Main Windows**: Inherit from QMainWindow, single instance pattern
- **Dialogs**: Inherit from QDialog, modal/modeless as needed
- **State Persistence**: Save/restore geometry, splitter positions
- **Settings**: Use QSettings for persistent configuration

## Custom Widget Pattern
- **Inheritance**: Inherit from appropriate Qt base class
- **Composition**: Embed child widgets, avoid deep inheritance
- **Signals**: Define custom signals for widget communication
- **Properties**: Use Qt property system for data binding
- **Encapsulation**: Hide internal implementation, expose clean API

## Signal/Slot System
- **Type Safety**: Use typed signals `pyqtSignal(int, str)`
- **Connection**: Connect in dedicated setup method
- **Slot Decoration**: Use `@pyqtSlot()` for performance
- **Cleanup**: Disconnect signals in cleanup methods
- **Documentation**: Document signal/slot relationships

## Resource Management
- **Icons**: Centralized icon loading with caching
- **Stylesheets**: QSS files for theming, hot-reloadable
- **Translations**: Qt's internationalization system
- **Memory**: Proper cleanup with `deleteLater()`
- **Files**: Resource files (.qrc) for bundling assets

## Error Handling Strategy
- **Global Handler**: Centralized error dialog system
- **Logging**: Qt logging categories for different modules
- **User Feedback**: Clear error messages, recovery options
- **Graceful Degradation**: Fallback behavior for failures
- **State Recovery**: Auto-save user work, crash recovery

## Performance Guidelines
- **Lazy Loading**: Load UI components on demand
- **Caching**: Cache expensive operations (icons, calculations)
- **Model/View**: Use for large data sets (QAbstractItemModel)
- **Updates**: Batch UI updates, use update regions
- **Threading**: Keep GUI thread responsive, offload work

## UI/UX Patterns
- **Consistency**: Standard icons, colors, spacing throughout
- **Feedback**: Loading states, progress indicators, status updates
- **Accessibility**: Keyboard navigation, screen reader support
- **Responsiveness**: Adaptive layouts, proper sizing policies
- **Theming**: Support system themes, custom styling

## Testing Approach
- **Unit Tests**: Test business logic, model classes
- **Widget Tests**: Use QTest framework for UI interactions
- **Integration**: Test signal/slot connections, workflows
- **Fixtures**: Reusable test components, mock objects
- **Automation**: Continuous testing with GUI test runners

## Best Practices
- Follow Qt naming conventions for custom classes
- Use layouts instead of absolute positioning
- Implement proper focus management and tab order
- Handle high DPI displays correctly
- Separate UI logic from business logic
- Use composition over inheritance for complex widgets
- Implement proper cleanup in destructors
- Document signal/slot relationships clearly
- Test UI components with appropriate frameworks
- Follow platform-specific UI guidelines
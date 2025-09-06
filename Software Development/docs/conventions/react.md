# React Conventions

## Project Structure
```
src/
├── components/ui/          # Reusable UI
├── components/features/    # Feature-specific
├── hooks/                  # Custom hooks
├── contexts/               # React contexts
├── services/               # API services
└── utils/                  # Utilities
```

## Component Patterns

### Standard Component
```jsx
const Component = ({ prop1, onAction }) => {
  const [state, setState] = useState(initial);
  
  useEffect(() => {
    // Side effects
    return cleanup;
  }, [deps]);

  return <div>{content}</div>;
};

Component.propTypes = {
  prop1: PropTypes.string.isRequired,
  onAction: PropTypes.func.isRequired
};
```

### Folder Structure
```
Component/
├── Component.jsx
├── Component.module.css
├── Component.test.jsx
└── index.js
```

## Custom Hooks

### API Hook
```jsx
const useApi = (endpoint, options) => {
  // Returns: { data, loading, error, refetch }
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  return { data, loading, error, refetch };
};
```

### Local Storage Hook
```jsx
const useLocalStorage = (key, initialValue) => {
  // Returns: [storedValue, setValue]
  // Handles JSON serialization/deserialization
};
```

## Context Pattern

```jsx
const AuthContext = createContext();

const authReducer = (state, action) => {
  // LOGIN_START, LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const login = async (credentials) => { /* impl */ };
  const logout = () => { /* impl */ };
  
  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

## State Management

```jsx
// Simple state
const [value, setValue] = useState(initial);

// Object state
const [form, setForm] = useState({ name: '', email: '' });
const handleChange = (e) => {
  const { name, value } = e.target;
  setForm(prev => ({ ...prev, [name]: value }));
};

// Complex state
const [state, dispatch] = useReducer(reducer, initialState);
// Actions: FETCH_START, FETCH_SUCCESS, FETCH_ERROR, ADD_ITEM, UPDATE_ITEM, DELETE_ITEM
```

## API Service

```jsx
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Add auth interceptors
apiClient.interceptors.request.use(addAuthToken);
apiClient.interceptors.response.use(handleResponse, handleError);

export const api = {
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  delete: (url, config) => apiClient.delete(url, config)
};
```

## Styling

### CSS Modules
```css
.container { /* Base styles */ }
.title { /* Typography */ }
.button { /* Interactive */ }
.button:hover { /* States */ }
.button:disabled { /* Disabled */ }
```

### CSS Variables
```css
:root {
  --primary: #007bff;
  --text: #212529;
  --bg: #ffffff;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --radius: 4px;
  --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

## Form Handling

```jsx
const Form = ({ onSubmit }) => {
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    // Return boolean, set errors
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

## Error Handling

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }

  render() {
    return this.state.hasError ? <ErrorUI /> : this.props.children;
  }
}
```

## Testing

```jsx
// Component tests
describe('Component', () => {
  test('renders', () => {
    render(<Component />);
    expect(screen.getByText('text')).toBeInTheDocument();
  });

  test('handles click', () => {
    const onClick = jest.fn();
    render(<Component onClick={onClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalled();
  });
});

// Hook tests
describe('useHook', () => {
  test('returns values', () => {
    const { result } = renderHook(() => useHook(params));
    expect(result.current).toEqual(expected);
  });
});
```

## Performance

```jsx
// Memoization
const Memo = memo(Component, (prev, next) => prev.id === next.id);

const Optimized = ({ items, filter }) => {
  const filtered = useMemo(() => 
    items.filter(item => item.name.includes(filter)), 
    [items, filter]
  );

  const handleClick = useCallback((item) => {
    // Handle click
  }, []);

  return <div>{/* render */}</div>;
};
```

## Best Practices

### Component Organization
- Single responsibility
- Functional components + hooks
- PropTypes for validation
- Barrel exports

### State Management
- Local state for component data
- Context for global state
- External libs for complex state
- Lift state up when shared

### Performance
- React.memo for expensive renders
- useCallback/useMemo for expensive ops
- Lazy loading for large components
- Avoid inline objects/functions

### Code Quality
- ESLint + Prettier
- Test critical paths
- Meaningful names
- Components < 200 lines
- Document complex logic

### Security
- Sanitize inputs
- HTTPS for APIs
- Secure storage
- Validate client + server
- Environment variables

## Environment
```bash
# .env
REACT_APP_API_URL=http://localhost:3001
REACT_APP_PROJECT_NAME=my-app
REACT_APP_STAGE=dev
```
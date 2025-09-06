# Next.js Development Conventions

## Project Structure (App Router)
```
src/
├── app/
│   ├── globals.css
│   ├── layout.js
│   ├── page.js
│   ├── loading.js
│   ├── error.js
│   ├── not-found.js
│   ├── (auth)/              # Route groups
│   │   ├── login/
│   │   │   └── page.js
│   │   └── register/
│   │       └── page.js
│   ├── dashboard/
│   │   ├── page.js
│   │   ├── layout.js
│   │   └── [id]/
│   │       └── page.js
│   └── api/                 # API routes
│       ├── auth/
│       │   └── route.js
│       └── users/
│           └── route.js
├── components/
│   ├── ui/
│   ├── layout/
│   └── features/
├── lib/
│   ├── auth.js
│   ├── db.js
│   └── utils.js
├── hooks/
├── contexts/
├── styles/
└── types/                   # TypeScript types
```

## Environment Configuration
```bash
# .env.local
NEXT_PUBLIC_PROJECT_NAME=my-awesome-app
NEXT_PUBLIC_STAGE=dev
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Server-side only
DATABASE_URL=postgresql://user:password@localhost:5432/db
JWT_SECRET=your-secret-key
API_KEY=your-api-key
```

## App Router Patterns

### Root Layout
```jsx
// app/layout.js
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: {
    template: '%s | My App',
    default: 'My App'
  },
  description: 'Application description',
  keywords: ['nextjs', 'react', 'app'],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Page Component
```jsx
// app/dashboard/page.js
import { Suspense } from 'react';
import { DashboardContent } from '@/components/features/dashboard/DashboardContent';
import { DashboardSkeleton } from '@/components/features/dashboard/DashboardSkeleton';

export const metadata = {
  title: 'Dashboard',
  description: 'User dashboard'
};

export default async function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardContent />
      </Suspense>
    </div>
  );
}
```

### Dynamic Routes
```jsx
// app/users/[id]/page.js
import { notFound } from 'next/navigation';
import { getUser } from '@/lib/api';

export async function generateMetadata({ params }) {
  const user = await getUser(params.id);
  
  if (!user) return { title: 'User Not Found' };
  
  return {
    title: `${user.name} - User Profile`,
    description: `Profile page for ${user.name}`
  };
}

export default async function UserPage({ params }) {
  const user = await getUser(params.id);
  
  if (!user) {
    notFound();
  }
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

## Server Components vs Client Components

### Server Component (Default)
```jsx
// app/posts/page.js
import { getPosts } from '@/lib/api';

export default async function PostsPage() {
  const posts = await getPosts();
  
  return (
    <div>
      <h1>Posts</h1>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  );
}
```

### Client Component
```jsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export default function InteractiveComponent() {
  const [count, setCount] = useState(0);
  const { user } = useAuth();
  
  useEffect(() => {
    // Client-side effects
  }, []);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

## API Routes

### GET Route
```js
// app/api/users/route.js
import { NextResponse } from 'next/server';
import { getUsers } from '@/lib/db';
import { auth } from '@/lib/auth';

export async function GET(request) {
  try {
    const session = await auth(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    
    const users = await getUsers({ page, limit });
    
    return NextResponse.json(users);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

### POST Route
```js
// app/api/users/route.js
import { NextResponse } from 'next/server';
import { createUser } from '@/lib/db';
import { auth } from '@/lib/auth';
import { userSchema } from '@/lib/validations';

export async function POST(request) {
  try {
    const session = await auth(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    const body = await request.json();
    const validatedData = userSchema.parse(body);
    
    const user = await createUser(validatedData);
    
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    if (error.name === 'ZodError') {
      return NextResponse.json(
        { error: 'Validation Error', details: error.errors },
        { status: 400 }
      );
    }
    
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

### Dynamic API Routes
```js
// app/api/users/[id]/route.js
import { NextResponse } from 'next/server';
import { getUser, updateUser, deleteUser } from '@/lib/db';

export async function GET(request, { params }) {
  try {
    const user = await getUser(params.id);
    
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

export async function PUT(request, { params }) {
  try {
    const body = await request.json();
    const user = await updateUser(params.id, body);
    
    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request, { params }) {
  try {
    await deleteUser(params.id);
    return NextResponse.json({ message: 'User deleted successfully' });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

## Data Fetching Patterns

### Server-Side Data Fetching
```jsx
// app/posts/[slug]/page.js
import { cache } from 'react';
import { getPost, getComments } from '@/lib/api';

// Cache the function to avoid duplicate requests
const getCachedPost = cache(async (slug) => {
  return await getPost(slug);
});

export default async function PostPage({ params }) {
  // Fetch data in parallel
  const [post, comments] = await Promise.all([
    getCachedPost(params.slug),
    getComments(params.slug)
  ]);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
      <CommentSection comments={comments} />
    </article>
  );
}
```

### Client-Side Data Fetching
```jsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export default function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const { session } = useAuth();
  
  useEffect(() => {
    if (!session) return;
    
    const fetchUser = async () => {
      try {
        const response = await fetch('/api/user/profile');
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, [session]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{user?.name}</h1>
      <p>{user?.email}</p>
    </div>
  );
}
```

## Middleware
```js
// middleware.js
import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function middleware(request) {
  const { pathname } = request.nextUrl;
  
  // Auth protection
  if (pathname.startsWith('/dashboard')) {
    const session = await auth(request);
    
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }
  
  // API rate limiting
  if (pathname.startsWith('/api/')) {
    const ip = request.ip || 'unknown';
    const rateLimit = await checkRateLimit(ip);
    
    if (!rateLimit.success) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      );
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*']
};
```

## Static Generation & Revalidation

### Static Site Generation
```jsx
// app/blog/[slug]/page.js
export async function generateStaticParams() {
  const posts = await getPosts();
  
  return posts.map(post => ({
    slug: post.slug
  }));
}

export default async function BlogPost({ params }) {
  const post = await getPost(params.slug);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

### Incremental Static Regeneration
```jsx
// app/products/page.js
export const revalidate = 3600; // Revalidate every hour

export default async function ProductsPage() {
  const products = await getProducts();
  
  return (
    <div>
      <h1>Products</h1>
      {products.map(product => (
        <div key={product.id}>
          <h2>{product.name}</h2>
          <p>${product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

## Error Handling

### Error Boundary
```jsx
// app/error.js
'use client';

import { useEffect } from 'react';

export default function Error({ error, reset }) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);
  
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>
        Try again
      </button>
    </div>
  );
}
```

### Global Error Handler
```jsx
// app/global-error.js
'use client';

export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  );
}
```

## Loading States
```jsx
// app/dashboard/loading.js
export default function Loading() {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p>Loading dashboard...</p>
    </div>
  );
}
```

## Image Optimization
```jsx
import Image from 'next/image';

export default function ProfileImage({ user }) {
  return (
    <Image
      src={user.avatar || '/default-avatar.png'}
      alt={`${user.name}'s avatar`}
      width={100}
      height={100}
      priority={true}
      className="rounded-full"
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
    />
  );
}
```

## Custom Hooks for Next.js

### useLocalStorage Hook
```jsx
'use client';

import { useState, useEffect } from 'react';

export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}
```

### useDebounce Hook
```jsx
'use client';

import { useState, useEffect } from 'react';

export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## Performance Optimization

### Bundle Analysis
```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    bundlePagesExternals: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  images: {
    domains: ['example.com', 'api.example.com'],
    formats: ['image/webp', 'image/avif'],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
```

### Dynamic Imports
```jsx
import dynamic from 'next/dynamic';

const DynamicComponent = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <p>Loading...</p>,
    ssr: false
  }
);

export default function Page() {
  return (
    <div>
      <DynamicComponent />
    </div>
  );
}
```

## Best Practices

### File Organization
- Use the App Router for new projects
- Co-locate related files in feature directories
- Use TypeScript for better type safety
- Keep components small and focused
- Use server components by default, client components when needed

### Performance
- Use Next.js Image component for image optimization
- Implement proper caching strategies
- Use dynamic imports for large components
- Optimize bundle size with webpack analysis

### SEO
- Use proper metadata in layout and page components
- Implement structured data where appropriate
- Use semantic HTML elements
- Optimize images with alt text and proper sizing

### Security
- Validate all user inputs
- Use environment variables for sensitive data
- Implement proper authentication and authorization
- Use HTTPS in production
- Sanitize data before rendering

### Development
- Use ESLint and Prettier for code consistency
- Implement proper error boundaries
- Use TypeScript for better developer experience
- Write tests for critical functionality
- Use proper Git workflow and commit messages
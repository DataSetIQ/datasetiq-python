# Website Integration Guide

## Add Python Library to Main Site

### 1. Navigation Link

Add to main navigation menu:

```tsx
// apps/web/src/components/layout/Header.tsx or similar
<NavigationItem 
  href="/docs/python" 
  icon={<PythonIcon />}
>
  Python Library
</NavigationItem>
```

### 2. Create Quickstart Page

Create `/docs/python` page:

**File:** `apps/web/src/app/docs/python/page.tsx`

```tsx
export default function PythonDocsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1>DataSetIQ Python Client</h1>
      
      <section className="my-8">
        <h2>Installation</h2>
        <pre><code>pip install datasetiq</code></pre>
      </section>
      
      <section className="my-8">
        <h2>Quick Start</h2>
        <pre><code>{`import datasetiq as iq

# Set your API key
iq.set_api_key("your-key-here")

# Get data as Pandas DataFrame
df = iq.get("fred-cpi")
print(df.head())`}</code></pre>
      </section>
      
      <section className="my-8">
        <h2>Features</h2>
        <ul>
          <li>40M+ time series datasets</li>
          <li>Pandas-ready DataFrames</li>
          <li>Intelligent caching</li>
          <li>Automatic retry logic</li>
          <li>Free tier available</li>
        </ul>
      </section>
      
      <section className="my-8">
        <h2>Documentation</h2>
        <p>
          Full documentation available on{" "}
          <a href="https://github.com/DataSetIQ/datasetiq-python">GitHub</a>
        </p>
      </section>
    </div>
  );
}
```

### 3. Add to Homepage

Add Python code example to homepage hero/features section:

```tsx
// apps/web/src/app/page.tsx
<CodeExample language="python">
{`import datasetiq as iq

# Get Consumer Price Index
cpi = iq.get("fred-cpi", start="2020-01-01")

# Calculate inflation
cpi['yoy_inflation'] = cpi['value'].pct_change(12) * 100

# Plot
cpi['yoy_inflation'].plot()`}
</CodeExample>
```

### 4. Update API Keys Page

Add Python instructions to API keys dashboard:

```tsx
// apps/web/src/app/dashboard/api-keys/page.tsx
<section className="mt-6">
  <h3>Using in Python</h3>
  <pre><code>{`pip install datasetiq

import datasetiq as iq
iq.set_api_key("${apiKey}")`}</code></pre>
</section>
```

### 5. Add PyPI Badge to Footer

```tsx
// Footer component
<a href="https://pypi.org/project/datasetiq/">
  <img src="https://badge.fury.io/py/datasetiq.svg" alt="PyPI version" />
</a>
```

### 6. SEO Updates

Update metadata to include Python-related keywords:

```tsx
// app/layout.tsx or metadata config
keywords: [
  "economic data",
  "time series",
  "python library",
  "pandas",
  "datasetiq python",
  "fred api python",
  // ... existing keywords
]
```

### 7. Blog Post (Optional)

Create announcement blog post:

**Title:** "Introducing DataSetIQ Python Library: 40M+ Time Series, 5 Lines of Code"

**Content:**
- Problem: Accessing economic data is painful
- Solution: `pip install datasetiq`
- Demo: Live code example
- Features: Pandas-ready, caching, free tier
- CTA: Try it now

### 8. Analytics Tracking

Add events to track Python library adoption:

```typescript
// Track Python library page views
analytics.track('python_docs_viewed');

// Track pip install command copies
analytics.track('install_command_copied', {
  source: 'docs'
});

// Track API key usage from Python
// (Already tracked in backend via User-Agent: datasetiq-python/0.1.0)
```

### 9. Email Templates

Update welcome email to mention Python library:

```html
<p>
  <strong>Python Developer?</strong> Install our library:<br>
  <code>pip install datasetiq</code>
</p>
```

### 10. Social Media

**Tweet Template:**
```
🐍 Introducing DataSetIQ Python Library!

Access 40M+ economic time series with just:

pip install datasetiq

✨ Pandas-ready DataFrames
✨ Free tier available
✨ 5 lines of code to insights

Docs: github.com/DataSetIQ/datasetiq-python

#Python #DataScience #Economics
```

**LinkedIn Post:**
```
Excited to announce the DataSetIQ Python library! 

Data scientists and analysts can now access 40M+ economic time series with a simple `pip install datasetiq`.

Key features:
• Returns pandas DataFrames (no JSON wrangling!)
• Intelligent caching for fast repeated queries
• Free tier: 25 RPM + 25 AI insights/month
• Automatic retry logic for production reliability

Perfect for:
📊 Economic research
📈 Financial modeling  
🤖 ML feature engineering
📉 Market analysis

Try it: github.com/DataSetIQ/datasetiq-python

#Python #DataScience #OpenSource
```

---

## Monitoring Success

Track these metrics after launch:

### Week 1
- [ ] PyPI downloads
- [ ] GitHub stars
- [ ] New signups with User-Agent: datasetiq-python
- [ ] 401/429 errors from Python lib (conversion opportunities)

### Month 1
- [ ] Monthly active Python users
- [ ] Conversion rate: anonymous → authenticated
- [ ] Conversion rate: free → paid (from Python users)
- [ ] Top error types (improve error messages)

### Ongoing
- [ ] Issues/PRs on GitHub
- [ ] Feature requests
- [ ] Python version distribution (should we drop 3.9 support?)
- [ ] Most popular datasets accessed via Python

---

**Need help with any of these integrations?** Let me know!

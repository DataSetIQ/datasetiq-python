# 🚀 PyPI Publishing Guide

## Current Status

✅ Package built successfully:
- `dist/datasetiq-0.1.0.tar.gz` (source distribution)
- `dist/datasetiq-0.1.0-py3-none-any.whl` (wheel)

✅ GitHub repository created:
- https://github.com/DataSetIQ/datasetiq-python

## Publishing to PyPI

### Option 1: Test on TestPyPI First (Recommended)

This allows you to test the package installation without affecting the production PyPI.

```bash
cd /Users/darshil/Desktop/DataSetIQ/Code/datasetiq-python

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your TestPyPI API token>

# Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ datasetiq

# Test it works
python3 -c "import datasetiq as iq; print(iq.__version__)"
```

### Option 2: Publish to Production PyPI

Once you're confident everything works:

```bash
cd /Users/darshil/Desktop/DataSetIQ/Code/datasetiq-python

# Upload to PyPI
python3 -m twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your PyPI API token>
```

## Getting API Tokens

### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Scope: "Entire account" or limit to "datasetiq" project
4. Copy the token (starts with `pypi-`)

### For Production PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Scope: "Entire account" or limit to "datasetiq" project
4. Copy the token

## Storing Credentials (Optional)

Create `~/.pypirc` to avoid entering credentials each time:

```ini
[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
username = __token__
password = pypi-your-test-token-here
```

**⚠️ Security Note:** Keep this file private! Consider using `keyring` instead for better security.

## After Publishing

### 1. Verify Installation
```bash
pip install datasetiq
python3 -c "import datasetiq as iq; print(iq.__version__)"
```

### 2. Update README Badge
The PyPI badge will automatically show the correct version once published.

### 3. Create GitHub Release
```bash
cd /Users/darshil/Desktop/DataSetIQ/Code/datasetiq-python
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
git push origin v0.1.0

# Or use GitHub CLI:
gh release create v0.1.0 dist/* --title "v0.1.0 - Initial Release" --notes "See CHANGELOG.md for details"
```

### 4. Announce!
- Tweet: "Introducing @DataSetIQ Python client 🐍 Access 40M+ economic time series with pandas-ready DataFrames. Free tier available! pip install datasetiq"
- Add to main website navigation
- Create `/docs/python` quickstart page
- Share in relevant communities (r/Python, r/datascience, etc.)

## Monitoring

### PyPI Stats
- https://pypistats.org/packages/datasetiq
- Downloads by version, Python version, OS

### GitHub Stats  
- https://github.com/DataSetIQ/datasetiq-python/pulse
- Stars, forks, traffic

### Backend Metrics
Track in your API:
- Anonymous API requests (trying before signup)
- 401/429 errors (conversion opportunities)
- Signup conversions from Python lib

## Troubleshooting

### "Invalid username/password"
- Make sure you're using `__token__` as the username (with two underscores)
- Paste the full token including the `pypi-` prefix

### "Package already exists"
- You can only upload each version once
- Bump version in `pyproject.toml` and rebuild

### "Invalid distribution"
- Check `pyproject.toml` formatting
- Verify all required fields are present
- Run `python3 -m build` again

## Next Steps After v0.1.0

### Future Enhancements (v0.2.0)
- [ ] Add `get_insight()` for AI-generated analysis
- [ ] Async support: `await iq.get_async()`
- [ ] Batch requests: `iq.get_many(["fred-cpi", "fred-gdp"])`
- [ ] Progress bars for large paginated fetches
- [ ] Export to Parquet/Arrow formats
- [ ] Caching to S3/cloud storage
- [ ] Date filtering for CSV endpoint (backend enhancement needed)

### Marketing Ideas
- [ ] Create Jupyter notebook tutorials
- [ ] Write blog post: "5 Lines of Python to Access 40M Time Series"
- [ ] Submit to Awesome Python lists
- [ ] Reach out to data science newsletters
- [ ] Create YouTube tutorial video
- [ ] Present at local Python meetup

---

**Ready to publish?** Run the commands above! 🎉

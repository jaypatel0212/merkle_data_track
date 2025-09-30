# Vercel Deployment Guide for Merkle Data Query Tool

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code needs to be in a GitHub repository
3. **Database Access**: Ensure your CockroachDB credentials are ready

## Project Structure

Your project should now have this structure:
```
Analyze Token Distribution/
├── api/
│   └── index.py              # Vercel serverless function entry point
├── script/
│   ├── templates/
│   │   └── index.html        # HTML template
│   └── merkle_web_app.py     # Original Flask app (not used in Vercel)
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Step-by-Step Deployment

### 1. Push to GitHub

First, initialize a Git repository and push your code to GitHub:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit for Vercel deployment"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Set up and deploy? `Y`
   - Which scope? Choose your account
   - Link to existing project? `N`
   - Project name: `merkle-query-tool` (or your preferred name)
   - Directory: `.` (current directory)

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Framework Preset: `Other`
   - Root Directory: `.`
   - Build Command: Leave empty
   - Output Directory: Leave empty

### 3. Configure Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `CRDB_URL` | Your CockroachDB connection string | Database connection URL |
| `CRDB_TABLE` | `public.merkle` | Database table name |

**Example CRDB_URL**:
```
postgresql://username:password@host:port/database?sslmode=require
```

### 4. Redeploy

After adding environment variables:

1. Go to the "Deployments" tab
2. Click the three dots on the latest deployment
3. Select "Redeploy"

Or trigger a new deployment by pushing to your GitHub repository.

## Testing Your Deployment

1. Visit your Vercel URL (e.g., `https://your-project-name.vercel.app`)
2. Test the query functionality with a valid creator address
3. Verify that the database connection works

## Troubleshooting

### Common Issues

1. **Template Not Found Error**:
   - Ensure `templates/index.html` is in the correct location
   - Check the template path in `api/index.py`

2. **Database Connection Error**:
   - Verify your `CRDB_URL` environment variable
   - Check if CockroachDB allows connections from Vercel's IP ranges
   - Ensure SSL is properly configured

3. **Import Errors**:
   - Make sure all dependencies are in `requirements.txt`
   - Check that `psycopg2-binary` is used instead of `psycopg2`

4. **Function Timeout**:
   - Vercel has a 10-second timeout for hobby plans
   - Optimize your database queries
   - Consider upgrading to Pro plan for longer timeouts

### Debugging

1. **Check Vercel Function Logs**:
   - Go to your project dashboard
   - Click on "Functions" tab
   - View logs for any errors

2. **Test Locally**:
   ```bash
   vercel dev
   ```
   This runs your app locally with Vercel's environment.

## Custom Domain (Optional)

1. Go to your project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Performance Optimization

1. **Database Connection Pooling**: Consider using connection pooling for better performance
2. **Caching**: Implement caching for frequently accessed data
3. **Query Optimization**: Optimize your SQL queries for better performance

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **Database Access**: Use read-only database users if possible
3. **Input Validation**: Ensure proper validation of user inputs
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## Support

- Vercel Documentation: [vercel.com/docs](https://vercel.com/docs)
- Vercel Community: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- Flask Documentation: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---

**Note**: This deployment uses Vercel's serverless functions, which means your app will scale automatically and you only pay for what you use. The free tier includes 100GB bandwidth and 100GB-hours of serverless function execution per month.

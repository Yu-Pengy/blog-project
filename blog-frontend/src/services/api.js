const API_BASE_URL = import.meta.env.PROD ? '/api' : 'http://localhost:5000/api';  // 开发环境

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // 重要：包含cookies用于session
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || data.error || 'API请求失败');
      }
      
      return data;
    } catch (error) {
      console.error('API请求错误:', error);
      throw error;
    }
  }

  // 认证相关
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout() {
    return this.request('/auth/logout', { method: 'POST' });
  }

  async register(username, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getCurrentUser() {
    return this.request('/auth/user');
  }

  // 头像上传方法
  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `${API_BASE_URL}/user/avatar`;
    const config = {
      method: 'POST',
      body: formData,
      credentials: 'include', // 包含cookies用于session
      // 注意：不要设置Content-Type，让浏览器自动设置
    };

    try {
      const response = await fetch(url, config);
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || data.error || '头像上传失败');
      }
      
      return data;
    } catch (error) {
      console.error('头像上传错误:', error);
      throw error;
    }
  }

  // 通用HTTP方法
  async get(endpoint, options = {}) {
    const { params, ...otherOptions } = options;
    let url = endpoint;
    
    // 如果有查询参数，添加到URL
    if (params) {
      const searchParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          searchParams.append(key, params[key]);
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += (url.includes('?') ? '&' : '?') + queryString;
      }
    }
    
    return this.request(url, { method: 'GET', ...otherOptions });
  }

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options
    });
  }

  // 文章相关
  async getPosts(categoryId = null, page = 1, perPage = 7) {
    const params = new URLSearchParams();
    if (categoryId) params.append('category_id', categoryId);
    if (page) params.append('page', page);
    if (perPage) params.append('per_page', perPage);
    
    const query = params.toString() ? `?${params.toString()}` : '';
    const url = `/posts${query}`;
    
    const result = await this.request(url);
    return result;
  }

  async getPost(id) {
    return this.request(`/posts/${id}`);
  }

  async getMyPosts() {
    return this.request('/my-posts');
  }

  async createPost(postData) {
    return this.request('/posts', {
      method: 'POST',
      body: JSON.stringify(postData),
    });
  }

  async updatePost(id, postData) {
    return this.request(`/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(postData),
    });
  }

  async deletePost(id) {
    return this.request(`/posts/${id}`, { method: 'DELETE' });
  }

  // 分类相关
  async getCategories() {
    return this.request('/categories');
  }

  // 评论相关
  async getComments(postId) {
    return this.request(`/posts/${postId}/comments`);
  }

  async createComment(postId, commentData) {
    return this.request(`/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify(commentData),
    });
  }

  async updateComment(commentId, commentData) {
    return this.request(`/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify(commentData),
    });
  }

  async deleteComment(commentId) {
    return this.request(`/comments/${commentId}`, { method: 'DELETE' });
  }

  // 统计相关
  async getStats() {
    return this.request('/stats');
  }

  // 管理员相关
  async getAdminPosts() {
    return this.request('/admin/posts');
  }

  async getAdminUsers() {
    return this.request('/admin/users');
  }

  async getAdminComments() {
    try {
      const result = await this.request('/admin/comments');
      
      // 如果返回的是对象，可能评论数据在某个属性中
      if (result && typeof result === 'object') {
        
        // 常见的返回格式：{ data: [...] } 或 { comments: [...] }
        if (result.data && Array.isArray(result.data)) {
          return result.data;
        }
        if (result.comments && Array.isArray(result.comments)) {
          return result.comments;
        }
        if (result.results && Array.isArray(result.results)) {
          return result.results;
        }
      }
      
      // 如果直接是数组，直接返回
      if (Array.isArray(result)) {
        return result;
      }
      
      console.warn('无法解析评论数据格式，返回空数组');
      return [];
    } catch (error) {
      console.error('管理员评论API调用失败:', error);
      // 如果API不存在（404错误），抛出特定错误
      if (error.message.includes('404') || error.message.includes('Not Found')) {
        console.log('管理员评论API不存在，将使用降级方案');
        throw new Error('ADMIN_COMMENTS_API_NOT_FOUND');
      }
      throw error;
    }
  }

  async deleteUser(id) {
    return this.request(`/admin/users/${id}`, { method: 'DELETE' });
  }
}

export default new ApiService();
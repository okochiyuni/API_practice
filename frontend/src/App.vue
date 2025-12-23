<script setup>
import { onMounted, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const categories = ref([])
const newCategory = ref('')
const isSubmitting = ref(false)
const isFetching = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const resetMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const fetchCategories = async () => {
  isFetching.value = true
  resetMessages()

  try {
    const response = await fetch(`${API_BASE}/categories`)

    if (!response.ok) {
      throw new Error('分類一覧の取得に失敗しました')
    }

    categories.value = await response.json()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '不明なエラーが発生しました'
  } finally {
    isFetching.value = false
  }
}

const addCategory = async () => {
  const name = newCategory.value.trim()
  if (!name) {
    errorMessage.value = '分類名を入力してください'
    return
  }

  isSubmitting.value = true
  resetMessages()

  try {
    const response = await fetch(`${API_BASE}/categories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => null)
      const detail = payload?.detail ?? '分類の登録に失敗しました'
      throw new Error(detail)
    }

    const created = await response.json()
    successMessage.value = `「${created.name}」を登録しました`
    newCategory.value = ''
    await fetchCategories()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '不明なエラーが発生しました'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <main class="page">
    <header class="page__header">
      <div>
        <p class="eyebrow">カテゴリー登録</p>
        <h1>タスク分類を先に登録できます</h1>
        <p class="lead">
          バックエンドは分類が登録されていないとタスクを追加できません。ここで分類を登録して、タスク登録の準備を整えてください。
        </p>
      </div>
    </header>

    <section class="card">
      <div class="card__header">
        <h2>新しい分類を追加</h2>
        <p class="muted">例: 仕事、学校、家庭</p>
      </div>
      <form class="form" @submit.prevent="addCategory">
        <label class="form__label" for="categoryName">分類名</label>
        <div class="form__row">
          <input
            id="categoryName"
            v-model="newCategory"
            type="text"
            name="category"
            placeholder="仕事"
            :disabled="isSubmitting"
            autocomplete="off"
          />
          <button type="submit" :disabled="isSubmitting">{{ isSubmitting ? '登録中…' : '登録する' }}</button>
        </div>
      </form>
      <p class="hint">* 同じ分類名は重複登録できません</p>
      <p v-if="successMessage" class="message message--success">{{ successMessage }}</p>
      <p v-if="errorMessage" class="message message--error">{{ errorMessage }}</p>
    </section>

    <section class="card">
      <div class="card__header">
        <h2>登録済みの分類</h2>
        <button class="ghost" type="button" :disabled="isFetching" @click="fetchCategories">
          {{ isFetching ? '更新中…' : '最新の情報を取得' }}
        </button>
      </div>
      <ul class="category-list">
        <li v-if="categories.length === 0" class="muted">まだ分類がありません。</li>
        <li v-for="category in categories" :key="category.name" class="category-list__item">
          <span class="pill">{{ category.name }}</span>
        </li>
      </ul>
    </section>
  </main>
</template>

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView, DeleteView
)
from .models import Recipe, Category
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
import logging

logger = logging.getLogger(__name__)


def about(request):
    context = {'title': 'О проекте'}
    return render(request, 'webapp/about.html', context)


class RecipeListView(ListView):
    """
    Отображает список объектов модели Recipe
    """
    model = Recipe
    template_name = 'webapp/home.html'
    context_object_name = 'recipes'
    ordering = ['-created_date']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeListView: {str(e)}")
            raise


class UserRecipeListView(ListView):
    """
    Отображает список объектов модели Recipe конкретного пользователя
    """
    model = Recipe
    template_name = 'webapp/user_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 5

    def get_queryset(self):
        try:
            user = get_object_or_404(User, username=self.kwargs.get('username'))
            return Recipe.objects.filter(author=user).order_by('-created_date')
        except Exception as e:
            logger.error(f"An error occurred in UserRecipeListView: {str(e)}")
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in UserRecipeListView: {str(e)}")
            raise


class RecipeByCategoryView(ListView):
    """
    Отображает список объектов модели Recipe по ключу выбранной модели Category
    """
    model = Recipe
    template_name = 'webapp/recipes_by_category.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        try:
            category = get_object_or_404(Category, id=self.kwargs['category_id'])
            return Recipe.objects.filter(category=category)
        except Exception as e:
            logger.error(f"An error occurred in RecipeByCategoryView: {str(e)}")
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['category'] = get_object_or_404(Category, id=self.kwargs['category_id'])
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeByCategoryView: {str(e)}")
            raise


class RecipeDetailView(DetailView):
    """
    Отображение подробной информации о конкретном объекте модели Recipe
    """
    model = Recipe

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeDetailView: {str(e)}")
            raise


class RecipeCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новых объектов модели Recipe,
    где автором будет текущий аутентифицированный пользователь
    """
    model = Recipe

    fields = ['title', 'category', 'description',
              'ingredients', 'cooking_steps',
              'cooking_time', 'active', 'image', ]

    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            form.instance.title = form.cleaned_data['title'].upper()
            result = super().form_valid(form)
            messages.success(self.request, f'Рецепт успешно добавлен.')
            return result
        except Exception as e:
            logger.error(f"An error occurred in RecipeCreateView: {str(e)}")
            messages.error(self.request, f'Произошла ошибка при сохранении рецепта.')
            raise

    def form_invalid(self, form):
        try:
            return super().form_invalid(form)
        except Exception as e:
            logger.error(f"An error occurred in RecipeCreateView: {str(e)}")
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeCreateView: {str(e)}")
            raise


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Обновление созданных объектов модели Recipe, при условии,
    что текущий пользователь является автором этих рецептов
    """
    model = Recipe
    fields = ['title', 'category', 'description',
              'ingredients', 'cooking_steps',
              'cooking_time', 'active', 'image', ]

    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            form.instance.title = form.cleaned_data['title'].upper()
            result = super().form_valid(form)
            messages.success(self.request, f'Рецепт успешно изменен.')
            return result
        except Exception as e:
            logger.error(f"An error occurred in RecipeUpdateView: {str(e)}")
            raise

    def test_func(self):
        # Проверка, что авторизованный пользователь является автором рецепта
        try:
            recipe = self.get_object()
            if self.request.user == recipe.author:
                return True
            return False
        except Exception as e:
            logger.error(f"An error occurred in RecipeUpdateView: {str(e)}")
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeUpdateView: {str(e)}")
            raise


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление объектов модели Recipe, при условии,
    что текущий пользователь является автором объекта
    """
    model = Recipe
    success_url = reverse_lazy('webapp-home')

    def test_func(self):
        # Проверка, что авторизованный пользователь является автором рецепта
        try:
            recipe = self.get_object()
            if self.request.user == recipe.author:
                return True
            return False
        except Exception as e:
            logger.error(f"An error occurred in RecipeDeleteView: {str(e)}")
            raise

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, f'Рецепт успешно удален.')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred in RecipeDeleteView: {str(e)}")
            messages.error(self.request, f'Произошла ошибка при удалении рецепта.')
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            return context
        except Exception as e:
            logger.error(f"An error occurred in RecipeDeleteView: {str(e)}")
            raise

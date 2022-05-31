from rest_framework.generics    import GenericAPIView
from rest_framework             import mixins


class RetrieveCreateUpdateAPIView(GenericAPIView,
                                  mixins.RetrieveModelMixin, 
                                  mixins.CreateModelMixin, 
                                  mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ListCreateDeleteAPIView(GenericAPIView,
                              mixins.ListModelMixin, 
                              mixins.CreateModelMixin, 
                              mixins.DestroyModelMixin):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

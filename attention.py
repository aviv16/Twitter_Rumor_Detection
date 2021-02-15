# from tensorflow.keras.layers import Dense, Lambda, dot, Activation, concatenate
# from tensorflow.keras.layers import Layer
#
#
# class attention(Layer):
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def __call__(self, hidden_states):
#         """
#         Many-to-one attention mechanism for Keras.
#         @param hidden_states: 3D tensor with shape (batch_size, time_steps, input_dim).
#         @return: 2D tensor with shape (batch_size, 128)
#         @author: felixhao28.
#         """
#         hidden_size = int(hidden_states.shape[2])
#         # Inside dense layer
#         #              hidden_states            dot               W            =>           score_first_part
#         # (batch_size, time_steps, hidden_size) dot (hidden_size, hidden_size) => (batch_size, time_steps, hidden_size)
#         # W is the trainable weight matrix of attention Luong's multiplicative style score
#         score_first_part = Dense(hidden_size, use_bias=False, name='attention_score_vec')(hidden_states)
#         #            score_first_part           dot        last_hidden_state     => attention_weights
#         # (batch_size, time_steps, hidden_size) dot   (batch_size, hidden_size)  => (batch_size, time_steps)
#         h_t = Lambda(lambda x: x[:, -1, :], output_shape=(hidden_size,), name='last_hidden_state')(hidden_states)
#         score = dot([score_first_part, h_t], [2, 1], name='attention_score')
#         attention_weights = Activation('softmax', name='attention_weight')(score)
#         # (batch_size, time_steps, hidden_size) dot (batch_size, time_steps) => (batch_size, hidden_size)
#         context_vector = dot([hidden_states, attention_weights], [1, 1], name='context_vector')
#         pre_activation = concatenate([context_vector, h_t], name='attention_output')
#         attention_vector = Dense(128, use_bias=False, activation='tanh', name='attention_vector')(pre_activation)
#         return attention_vector
# #
from tensorflow.keras.layers import Layer
import tensorflow.keras.backend as K

class attention(Layer):
    def __init__(self,**kwargs):
        super(attention,self).__init__(**kwargs)

    def build(self,input_shape):
        self.W=self.add_weight(name="att_weight",shape=(input_shape[-1],1),initializer="normal")
        self.b=self.add_weight(name="att_bias",shape=(input_shape[1],1),initializer="zeros")
        super(attention, self).build(input_shape)

    def call(self,x):
        et=K.squeeze(K.tanh(K.dot(x,self.W)+self.b),axis=-1)
        at=K.softmax(et)
        at=K.expand_dims(at,axis=-1)
        output=x*at
        return K.sum(output,axis=1)

    def compute_output_shape(self,input_shape):
        return (input_shape[0],input_shape[-1])

    def get_config(self):
        return super(attention,self).get_config()

# Flask

Como funciona:

Recebe solicitações HTTP do tipo GET ou POST.
Está sendo utilizando o POSTMAN para demonstrar o funcionamento.
As APIS utilizadas são:

## Login
Funciona mandando um request POST com um corpo em JSON com a seguite estrutura:
![image](https://user-images.githubusercontent.com/111078608/202823609-cccb8624-e388-4299-b63a-24121ae8548e.png)

No caso da tentativa de login ser bem sucedida, você irá receber uma respotas com os dados do usuário(exceto a senha) e a mensagem de logado.

![image](https://user-images.githubusercontent.com/111078608/202823678-8a9d413d-48fa-40f2-8772-39ec54031fa9.png)

No caso de uma tentativa, em que algum dos dados esteja errado, você ira se deparar com a seguinte mensagem resposta:

![image](https://user-images.githubusercontent.com/111078608/202823751-7edec65d-679c-4d1d-be11-417d7a3ff7ac.png)

## Logout

No caso do usuário estar logado, você pode realizar logout utilizando a rota /logout do servidor:

![image](https://user-images.githubusercontent.com/111078608/202824186-714eaa03-d4c3-415d-840a-1f65cc98f5a7.png)

## SignUp

Para criar contas:

![image](https://user-images.githubusercontent.com/111078608/202826728-2ec81002-f5b8-43e5-b119-01dfb8b92ce9.png)

## Check Tags

Funcao com o objetivo de enviar uma lista de tags e retornar as tags que estao registradas e as nao registradas, no caso de tags registradas é retornado todos os dados dessa tag

![image](https://user-images.githubusercontent.com/111078608/202826908-96bd4704-2234-48c3-910b-568998a3b9b2.png)

![image](https://user-images.githubusercontent.com/111078608/202826935-54786639-45b3-43cb-88cd-42e591fb2564.png)

## Reg Tags

Função com o objetivo de registar as tags:

![image](https://user-images.githubusercontent.com/111078608/202827832-8ee01e63-9dc2-448f-b31d-2c7ec0839bdb.png)

## Total tags
Função com o objetivo de retornar a quantidade de tags no geral e em cada categoria:

![image](https://user-images.githubusercontent.com/111078608/202827949-0a64d7b1-d77d-486c-be4e-b49192484ff8.png)

## Get Tags
Funcao que retorna todas as tags do DB com o objetivo de preencher o inventário:

![image](https://user-images.githubusercontent.com/111078608/202828034-bab14378-c56d-4727-a12e-e3578b691061.png)

## Get Log
Funcao que retornar o log de eventos:

![image](https://user-images.githubusercontent.com/111078608/202828086-83f268a7-9518-4ffd-a452-cf8f8ae8d592.png)

## Change Tags
Funcao feita para alterar dados das tags:

![image](https://user-images.githubusercontent.com/111078608/202828179-25a22c25-378b-4b1c-ac92-2e42cbad8f14.png)




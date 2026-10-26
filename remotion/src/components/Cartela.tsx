import React from "react";
import { COR, FONTE, ROTULO, SAFE } from "../brand";
import { FundoGrade } from "./FundoGrade";
import { Titulo } from "./Titulo";

export type CartelaProps = {
  /** Nível 1 (contexto). */
  nivel1?: string | null;
  /** Nível 2 (impacto). */
  nivel2?: string | null;
  cinza?: number;
  selecao?: string | null;
  rabisco?: string | null;
  corRabisco?: string | null;
  /** Rótulo pequeno no topo (ex.: "ANIMAÇÃO L08 · PENDENTE"). */
  rotulo?: string | null;
  estatico?: boolean;
  inicioRabisco?: number | null;
};

/** Card em tela cheia (#111 + grade) com níveis 1 e 2. */
export const Cartela: React.FC<CartelaProps> = ({
  nivel1,
  nivel2,
  cinza = 0,
  selecao = null,
  rabisco,
  corRabisco,
  rotulo,
  estatico,
  inicioRabisco,
}) => {
  return (
    <FundoGrade>
      {rotulo ? (
        <div
          style={{
            position: "absolute",
            top: SAFE.topo + 20,
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: FONTE.familia,
            fontSize: ROTULO.tamanho,
            fontWeight: ROTULO.peso,
            letterSpacing: ROTULO.tracking,
            color: COR.cinza,
            textTransform: "uppercase",
          }}
        >
          {rotulo}
        </div>
      ) : null}
      <Titulo
        contexto={nivel1}
        impacto={nivel2}
        cinza={cinza}
        selecao={selecao}
        rabisco={rabisco}
        corRabisco={corRabisco}
        posicao="centro"
        sombra={false}
        estatico={estatico}
        inicioRabisco={inicioRabisco}
      />
    </FundoGrade>
  );
};

import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Container,
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  Stack,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import { Agencia, listAgencias } from "../services/agencias";
import {
  ApiError,
  createUsuario,
  listDiretoriasPublic,
  type Diretoria,
} from "../services/usuarios";
import { useAuth } from "../store/auth";

type UserType = "bb" | "npbb" | "agencia";

export default function Register() {
  const navigate = useNavigate();
  const steps = ["Tipo de usuario", "Agencia", "Dados da conta"];

  const [activeStep, setActiveStep] = useState(0);
  const [skipped, setSkipped] = useState(new Set<number>());

  const [userType, setUserType] = useState<UserType | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [matriculaBB, setMatriculaBB] = useState("");
  const [diretoriaId, setDiretoriaId] = useState<string>("");
  const [agenciaId, setAgenciaId] = useState<string>("");
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [serverFieldErrors, setServerFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const { login: authLogin } = useAuth();

  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [agenciasLoading, setAgenciasLoading] = useState(false);
  const [agenciasError, setAgenciasError] = useState<string | null>(null);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [diretoriasLoading, setDiretoriasLoading] = useState(false);
  const [diretoriasError, setDiretoriasError] = useState<string | null>(null);

  const isAgency = userType === "agencia";
  const isStepOptional = (step: number) => step === 1 && !isAgency;
  const isStepSkipped = (step: number) => skipped.has(step);

  useEffect(() => {
    if (userType !== "agencia") {
      setAgenciasError(null);
      return;
    }

    setAgenciasLoading(true);
    setAgenciasError(null);
    listAgencias({ limit: 200 })
      .then((items) => setAgencias(items))
      .catch((err: any) => setAgenciasError(err?.message || "Erro ao carregar agencias"))
      .finally(() => setAgenciasLoading(false));
  }, [userType]);

  useEffect(() => {
    if (userType !== "bb") {
      setDiretoriasError(null);
      return;
    }

    setDiretoriasLoading(true);
    setDiretoriasError(null);
    listDiretoriasPublic()
      .then((items) => setDiretorias(items))
      .catch((err: any) => setDiretoriasError(err?.message || "Erro ao carregar diretorias"))
      .finally(() => setDiretoriasLoading(false));
  }, [userType]);

  const errors = useMemo(() => {
    const next: Record<string, string> = {};

    if (!userType) next.userType = "Selecione um tipo de usuario";

    const emailTrim = email.trim();
    if (!emailTrim) next.email = "Informe seu email";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailTrim)) next.email = "Email invalido";
    else if (userType === "bb" && !emailTrim.endsWith("@bb.com.br"))
      next.email = "Para BB, use email @bb.com.br";
    else if (userType === "npbb" && !emailTrim.endsWith("@npbb.com.br"))
      next.email = "Para NPBB, use email @npbb.com.br";
    else if (userType === "agencia" && agenciaId) {
      const selected = agencias.find((a) => String(a.id) === String(agenciaId));
      const emailDomain = emailTrim.split("@").pop()?.toLowerCase();
      const agencyDomain = selected?.dominio?.toLowerCase().replace(/^@/, "");
      const matchesDomain =
        emailDomain && agencyDomain && (emailDomain === agencyDomain || emailDomain.endsWith(`.${agencyDomain}`));
      if (emailDomain && agencyDomain && !matchesDomain) {
        next.email = `Para esta agencia, use email @${agencyDomain}`;
      }
    }

    if (!password) next.password = "Informe uma senha";
    else if (!/^(?=.*[A-Za-z])(?=.*\d).{6,}$/.test(password))
      next.password = "Minimo 6 caracteres, com letra e numero";

    if (!confirmPassword) next.confirmPassword = "Confirme sua senha";
    else if (confirmPassword !== password) next.confirmPassword = "As senhas nao coincidem";

    if (userType === "bb") {
      if (!diretoriaId) next.diretoriaId = "Selecione sua diretoria";
      if (!matriculaBB) next.matriculaBB = "Informe a matricula BB";
      else if (!/^[A-Za-z][0-9]{1,16}$/.test(matriculaBB))
        next.matriculaBB = "Formato invalido (ex.: A123)";
    }

    if (userType === "agencia" && !agenciaId) next.agenciaId = "Selecione uma agencia";

    return next;
  }, [userType, email, password, confirmPassword, matriculaBB, agenciaId, diretoriaId]);

  const canSubmit = Object.keys(errors).length === 0;
  const canContinueFromType = Boolean(userType);
  const canContinueFromAgency =
    Boolean(agenciaId) && !agenciasLoading && !agenciasError && agencias.some((a) => String(a.id) === agenciaId);

  const handleNext = () => {
    setSubmitAttempted(false);
    setSubmitError(null);
    if (activeStep === 0) {
      if (!userType) return;
      if (userType === "agencia") {
        const nextSkipped = new Set(skipped);
        nextSkipped.delete(1);
        setSkipped(nextSkipped);
        setActiveStep(1);
      } else {
        const nextSkipped = new Set(skipped);
        nextSkipped.add(1);
        setSkipped(nextSkipped);
        setActiveStep(2);
      }
      return;
    }
    if (activeStep === 1) {
      setActiveStep(2);
      return;
    }
  };

  const handleBack = () => {
    setSubmitAttempted(false);
    setSubmitError(null);
    if (activeStep === 2 && userType !== "agencia") {
      setActiveStep(0);
      return;
    }
    setActiveStep((prev) => Math.max(0, prev - 1));
  };

  const handleCreateAccount = async () => {
    setSubmitAttempted(true);
    setSubmitError(null);
    setServerFieldErrors({});
    if (!canSubmit || !userType) return;

    setSubmitting(true);
    try {
      await createUsuario({
        email: email.trim(),
        password,
        tipo_usuario: userType,
        ...(userType === "bb"
          ? { diretoria_id: Number(diretoriaId), matricula: matriculaBB.trim() }
          : {}),
        ...(userType === "agencia" ? { agencia_id: Number(agenciaId) } : {}),
      });

      await authLogin(email.trim(), password);
      navigate("/success", { replace: true });
    } catch (err: any) {
      if (err instanceof ApiError) {
        const detail = err.detail;
        const message =
          typeof detail === "string" ? detail : typeof detail?.message === "string" ? detail.message : err.message;
        const field = typeof detail === "object" ? detail?.field : undefined;

        setSubmitError(message);
        if (field) {
          const mappedField =
            field === "agencia_id"
              ? "agenciaId"
              : field === "matricula"
                ? "matriculaBB"
                : field === "diretoria_id"
                  ? "diretoriaId"
                  : field;
          setServerFieldErrors((prev) => ({ ...prev, [mappedField]: message }));
        }
      } else {
        setSubmitError(err?.message || "Nao foi possivel criar a conta");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Paper
        sx={{
          width: "100%",
          p: 4,
          borderRadius: 3,
          display: "flex",
          flexDirection: "column",
          gap: 3,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Criar nova conta
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Siga as etapas para criar sua conta.
          </Typography>
        </Box>

        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label, index) => (
            <Step key={label} completed={isStepSkipped(index) ? false : undefined}>
              <StepLabel
                optional={
                  isStepOptional(index) ? (
                    <Typography variant="caption" color="text.secondary">
                      opcional
                    </Typography>
                  ) : undefined
                }
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box
          component="form"
          onSubmit={(e) => {
            e.preventDefault();
            if (activeStep < 2) {
              handleNext();
              return;
            }
            handleCreateAccount();
          }}
          noValidate
        >
          <Stack spacing={2.5}>
            {activeStep === 0 && (
              <>
                <FormControl>
                  <FormLabel>Tipo de usuario</FormLabel>
                  <RadioGroup
                    value={userType ?? ""}
                    onChange={(e) => {
                      const next = e.target.value as UserType;
                      setUserType(next);
                      if (next !== "bb") setMatriculaBB("");
                      if (next !== "bb") setDiretoriaId("");
                      if (next !== "agencia") setAgenciaId("");
                      setSubmitAttempted(false);
                      setSubmitError(null);
                      setServerFieldErrors({});
                    }}
                  >
                    <FormControlLabel value="bb" control={<Radio />} label="Funcionario BB" />
                    <FormControlLabel value="npbb" control={<Radio />} label="Funcionario NPBB" />
                    <FormControlLabel value="agencia" control={<Radio />} label="Funcionario Agencia" />
                  </RadioGroup>
                </FormControl>

                <Box display="flex" justifyContent="space-between" gap={2}>
                  <Button
                    variant="text"
                    type="button"
                    onClick={() => {
                      navigate("/login");
                    }}
                  >
                    Voltar para login
                  </Button>
                  <Button
                    variant="contained"
                    type="button"
                    onClick={handleNext}
                    disabled={!canContinueFromType}
                  >
                    Continuar
                  </Button>
                </Box>
              </>
            )}

            {activeStep === 1 && (
              <>
                <Autocomplete
                  options={agencias}
                  loading={agenciasLoading}
                  value={
                    agencias.find((a) => a.id === (agenciaId ? Number(agenciaId) : -1)) ?? null
                  }
                  onChange={(_, value) => {
                    setAgenciaId(value ? String(value.id) : "");
                    setSubmitError(null);
                    setServerFieldErrors((prev) => {
                      const next = { ...prev };
                      delete next.agenciaId;
                      return next;
                    });
                  }}
                  getOptionLabel={(option) => option.nome}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  fullWidth
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Agencia"
                      placeholder="Pesquisar..."
                      error={Boolean(errors.agenciaId)}
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {agenciasLoading ? (
                              <CircularProgress color="inherit" size={18} />
                            ) : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                />
                  {errors.agenciaId && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                      {errors.agenciaId}
                    </Typography>
                  )}
                  {serverFieldErrors.agenciaId && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                      {serverFieldErrors.agenciaId}
                    </Typography>
                  )}
                  {agenciasError && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                      {agenciasError}
                    </Typography>
                  )}

                <Box display="flex" justifyContent="space-between" gap={2}>
                  <Button
                    variant="outlined"
                    type="button"
                    onClick={handleBack}
                  >
                    Voltar
                  </Button>
                  <Button
                    variant="contained"
                    type="button"
                    onClick={handleNext}
                    disabled={!canContinueFromAgency}
                  >
                    Continuar
                  </Button>
                </Box>
              </>
            )}

            {activeStep === 2 && (
              <>
                {submitAttempted && !canSubmit && (
                  <Alert severity="error" variant="filled">
                    Revise os campos destacados.
                  </Alert>
                )}

                {submitError && (
                  <Alert severity="error" variant="filled">
                    {submitError}
                  </Alert>
                )}

                <TextField
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setSubmitError(null);
                    setServerFieldErrors((prev) => {
                      const next = { ...prev };
                      delete next.email;
                      return next;
                    });
                  }}
                  required
                  fullWidth
                  error={Boolean(errors.email || serverFieldErrors.email)}
                  helperText={serverFieldErrors.email ?? errors.email}
                  autoComplete="email"
                />

                <TextField
                  label="Senha"
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setSubmitError(null);
                    setServerFieldErrors((prev) => {
                      const next = { ...prev };
                      delete next.password;
                      return next;
                    });
                  }}
                  required
                  fullWidth
                  error={Boolean(errors.password || serverFieldErrors.password)}
                  helperText={serverFieldErrors.password ?? errors.password}
                  autoComplete="new-password"
                />

                <TextField
                  label="Confirmar senha"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    setSubmitError(null);
                  }}
                  required
                  fullWidth
                  error={Boolean(errors.confirmPassword)}
                  helperText={errors.confirmPassword}
                  autoComplete="new-password"
                />

                {userType === "bb" && (
                  <>
                    <Autocomplete
                      options={diretorias}
                      loading={diretoriasLoading}
                      value={
                        diretorias.find((d) => d.id === (diretoriaId ? Number(diretoriaId) : -1)) ??
                        null
                      }
                      onChange={(_, value) => {
                        setDiretoriaId(value ? String(value.id) : "");
                        setSubmitError(null);
                        setServerFieldErrors((prev) => {
                          const next = { ...prev };
                          delete next.diretoriaId;
                          return next;
                        });
                      }}
                      getOptionLabel={(option) => option.nome}
                      isOptionEqualToValue={(option, value) => option.id === value.id}
                      fullWidth
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Diretoria"
                          placeholder="Selecione sua diretoria"
                          error={Boolean(errors.diretoriaId || serverFieldErrors.diretoriaId)}
                          InputProps={{
                            ...params.InputProps,
                            endAdornment: (
                              <>
                                {diretoriasLoading ? (
                                  <CircularProgress color="inherit" size={18} />
                                ) : null}
                                {params.InputProps.endAdornment}
                              </>
                            ),
                          }}
                        />
                      )}
                    />
                    {errors.diretoriaId && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                        {errors.diretoriaId}
                      </Typography>
                    )}
                    {serverFieldErrors.diretoriaId && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                        {serverFieldErrors.diretoriaId}
                      </Typography>
                    )}
                    {diretoriasError && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                        {diretoriasError}
                      </Typography>
                    )}
                    <TextField
                      label="Matricula BB"
                      value={matriculaBB}
                      onChange={(e) => {
                        setMatriculaBB(e.target.value);
                        setSubmitError(null);
                        setServerFieldErrors((prev) => {
                          const next = { ...prev };
                          delete next.matriculaBB;
                          return next;
                        });
                      }}
                      required
                      fullWidth
                      error={Boolean(errors.matriculaBB || serverFieldErrors.matriculaBB)}
                      helperText={serverFieldErrors.matriculaBB ?? errors.matriculaBB}
                    />
                  </>
                )}

                <Box display="flex" justifyContent="space-between" gap={2}>
                  <Button
                    variant="outlined"
                    type="button"
                    onClick={handleBack}
                  >
                    Voltar
                  </Button>
                  <Button
                    variant="contained"
                    size="large"
                    type="submit"
                    disabled={!canSubmit || submitting}
                  >
                    {submitting ? <CircularProgress size={22} color="inherit" /> : "Criar Conta"}
                  </Button>
                </Box>

                <Button
                  variant="text"
                  type="button"
                  onClick={() => {
                    navigate("/login");
                  }}
                  sx={{ alignSelf: "flex-start" }}
                >
                  Voltar para login
                </Button>
              </>
            )}
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
